import uuid
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastembed import SparseTextEmbedding
from qdrant_client import QdrantClient, models
from qdrant_client.models import (
    VectorParams, Distance, PointStruct,
    SparseVectorParams, SparseIndexParams,
    Filter, FieldCondition, MatchValue,
    PayloadSchemaType
)
from src.config import (
    ACTIVE_API_KEY, GEMINI_API_KEY, EMBEDDING_MODEL, EMBEDDING_DIM,
    TOP_K, QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION
)

if GEMINI_API_KEY:
    from google import genai
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)


class Qdrant:
    def __init__(self):
        self.qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self.collection_name = QDRANT_COLLECTION

        self.sparse_model = SparseTextEmbedding(model_name="Qdrant/bm25")

        self._setup_collection()

        self.documents: Dict[str, Dict[str, Any]] = {}
        self._load_document_metadata()

    def _setup_collection(self):
        needs_creation = False

        if not self.qdrant_client.collection_exists(self.collection_name):
            needs_creation = True
        else:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            sparse_config = collection_info.config.params.sparse_vectors
            if not sparse_config or "sparse" not in sparse_config:
                print(f"[Qdrant] Upgrading collection '{self.collection_name}' for hybrid search...")
                self.qdrant_client.delete_collection(self.collection_name)
                needs_creation = True

        if needs_creation:
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "dense": VectorParams(
                        size=EMBEDDING_DIM,
                        distance=Distance.COSINE
                    )
                },
                sparse_vectors_config={
                    "sparse": SparseVectorParams(
                        index=SparseIndexParams(on_disk=False)
                    )
                }
            )

        fields_to_index = {
            "document_id": PayloadSchemaType.KEYWORD,
            "filename": PayloadSchemaType.KEYWORD,
            "chunk_type": PayloadSchemaType.KEYWORD,
            "page": PayloadSchemaType.INTEGER,
            "uploaded_at": PayloadSchemaType.KEYWORD,
            "question": PayloadSchemaType.TEXT,
            "answer": PayloadSchemaType.TEXT,
        }

        for field_name, field_type in fields_to_index.items():
            try:
                self.qdrant_client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field_name,
                    field_schema=field_type
                )
            except Exception:
                pass

    def count_chunks(self):
        try:
            return self.qdrant_client.count(collection_name=self.collection_name).count
        except Exception:
            return 0

    def _load_document_metadata(self):
        offset = None
        seen_documents = set()

        while True:
            try:
                results, offset = self.qdrant_client.scroll(
                    collection_name=self.collection_name,
                    limit=500,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )
            except Exception:
                break

            if not results:
                break

            for point in results:
                doc_id = point.payload.get("document_id")
                if doc_id and doc_id not in seen_documents:
                    seen_documents.add(doc_id)
                    self.documents[doc_id] = {
                        "document_id": doc_id,
                        "filename": point.payload.get("filename", ""),
                        "total_pages": point.payload.get("total_pages", 0),
                        "total_chunks": point.payload.get("total_chunks", 0),
                        "created_at": point.payload.get("uploaded_at", ""),
                    }

            if offset is None:
                break

    def _get_dense_embedding(self, text: str):
        if GEMINI_API_KEY:
            try:
                result = gemini_client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=text
                )
                return result.embeddings[0].values
            except Exception as error:
                print(f"[Warning] Gemini Embedding API failed ({error}), using fallback.")
        elif ACTIVE_API_KEY:
            from openai import OpenAI
            try:
                client = OpenAI(api_key=ACTIVE_API_KEY)
                response = client.embeddings.create(input=text, model=EMBEDDING_MODEL)
                return response.data[0].embedding
            except Exception as error:
                print(f"[Warning] OpenAI Embedding API failed ({error}), using fallback.")

        rng = np.random.RandomState(abs(hash(text)) % (2**32))
        random_vector = rng.randn(EMBEDDING_DIM)
        normalized = random_vector / np.linalg.norm(random_vector)
        return normalized.tolist()

    def add_document(self, doc_data: Dict[str, Any]):
        doc_id = doc_data["document_id"]
        uploaded_at = datetime.now(timezone.utc).isoformat()

        doc_metadata = {
            "document_id": doc_id,
            "filename": doc_data["filename"],
            "total_pages": doc_data["total_pages"],
            "total_chunks": doc_data["total_chunks"],
            "created_at": uploaded_at
        }
        self.documents[doc_id] = doc_metadata

        chunks = doc_data.get("chunks", [])
        if not chunks:
            return doc_metadata

        chunk_texts = [chunk["content"] for chunk in chunks]
        sparse_embeddings = list(self.sparse_model.embed(chunk_texts))

        points = []
        for i, chunk in enumerate(chunks):
            point_id = str(uuid.uuid4())

            question_text = chunk.get("question", "")
            answer_text = chunk.get("answer", "")
            text_to_embed = question_text if question_text else chunk["content"]
            dense_embedding = self._get_dense_embedding(text_to_embed)

            sparse_emb = sparse_embeddings[i]

            payload = {
                "chunk_id": chunk["chunk_id"],
                "document_id": doc_id,
                "filename": doc_data["filename"],
                "page": chunk["page"],
                "end_page": chunk.get("end_page", chunk["page"]),
                "content": chunk["content"],
                "question": question_text,
                "answer": answer_text,
                "chunk_type": chunk.get("chunk_type", "recursive_character"),
                "uploaded_at": uploaded_at,
                "total_pages": doc_data["total_pages"],
                "total_chunks": doc_data["total_chunks"],
            }

            points.append(PointStruct(
                id=point_id,
                vector={
                    "dense": dense_embedding,
                    "sparse": models.SparseVector(
                        indices=sparse_emb.indices.tolist(),
                        values=sparse_emb.values.tolist(),
                    ),
                },
                payload=payload
            ))

        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=batch
            )

        return doc_metadata

    def get_document(self, doc_id: str):
        return self.documents.get(doc_id)

    def delete_document(self, doc_id: str) -> bool:
        if doc_id in self.documents:
            del self.documents[doc_id]
            self.qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="document_id",
                                match=models.MatchValue(value=doc_id),
                            ),
                        ],
                    )
                ),
            )
            return True
        return False

    def list_documents(self):
        return list(self.documents.values())

    def hybrid_search(
        self,
        query: str,
        top_k: int = TOP_K,
        document_id: Optional[str] = None,
        score_threshold: Optional[float] = None
    ):
        if self.count_chunks() == 0:
            return []

        dense_query_vector = self._get_dense_embedding(query)
        sparse_query = list(self.sparse_model.embed([query]))[0]

        search_filter = None
        if document_id:
            search_filter = Filter(must=[
                FieldCondition(key="document_id", match=MatchValue(value=document_id))
            ])

        prefetch_limit = max(top_k * 4, 20)

        prefetch_queries = [
            models.Prefetch(
                query=dense_query_vector,
                using="dense",
                limit=prefetch_limit,
                filter=search_filter,
            ),
            models.Prefetch(
                query=models.SparseVector(
                    indices=sparse_query.indices.tolist(),
                    values=sparse_query.values.tolist(),
                ),
                using="sparse",
                limit=prefetch_limit,
                filter=search_filter,
            ),
        ]

        try:
            hits = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                prefetch=prefetch_queries,
                query=models.FusionQuery(fusion=models.Fusion.RRF),
                limit=top_k,
                with_payload=True,
            ).points
        except Exception as error:
            print(f"[Qdrant] Hybrid search failed: {error}")
            return []

        results = []
        for hit in hits:
            score = float(hit.score or 0.0)
            if score_threshold is not None and score < score_threshold:
                continue

            payload = hit.payload or {}
            results.append({
                "chunk_id": payload.get("chunk_id", ""),
                "document_id": payload.get("document_id", ""),
                "filename": payload.get("filename", ""),
                "page": payload.get("page", 0),
                "content": payload.get("content", ""),
                "score": score,
            })

        return results


qdrant = Qdrant()
