# Production-Oriented RAG & LLM Tool-Calling Agent API

A lightweight, production-oriented Retrieval-Augmented Generation (RAG) and Tool-Calling Agent service built with FastAPI, PyPDF, Hybrid Search (Semantic + BM25 with Qdrant Native RRF), PostgreSQL persistence, and OpenAI Tool Calling.

---

## 1. High-Level Architecture Diagram

```
PDF Document Upload (POST /documents/upload)
        │
        ▼
Page-Level Text Extraction (pypdf)
        │
        ▼
Structured Q&A & Recursive Chunking
 (Detects Q1., Question 1:, 1. & merges cross-page cutoffs)
        │
        ▼
Hybrid Indexing (OpenAI Dense Embeddings + BM25 Sparse Keywords)
        │
        ▼
Qdrant Vector Database
        │
        ├─────────────────────────────────────────┐
        │                                         │
User Question (POST /chat)                       │
        │                                         │
        ▼                                         │
LLM Agent Execution Loop                          │
 (System Prompt + Anti-Hallucination Guardrails)  │
        │                                         │
        ├──────────► Tool Call 1: search_database ┴──► Qdrant Server-Side RRF Hybrid Search
        │                                                     │
        │                                                     ▼
        │                                              Top-K Chunks + Source Attribution
        │                                                     │
        ├──────────► Tool Call 2: create_issue_tickets ───────┼──► PostgreSQL Ticket Table
        │                                                     │
        ▼                                                     ▼
Final Response: { "answer": "...", "sources": [...], "tool_calls": [...] }
        │
        ▼
Saved to PostgreSQL (Conversations & Chat Messages)
```

---

## 2. Project Structure

```
rag_test/
├── main.py                     # FastAPI routes & app entry point
├── create_sample_pdf.py        # Generates sample policy PDF for testing
├── test_qdrant.py              # Qdrant hybrid search & RRF verification script
├── eval_suite.py               # Evaluation suite with OOB negative testing
├── alembic/                    # Database migration scripts
│   ├── versions/               # Migration revision files
│   └── env.py                  # Alembic environment config
├── src/
│   ├── config.py               # Central environment configuration
│   ├── models.py               # Pydantic request & response schemas
│   ├── pdf_processor.py        # PDF extraction, Q&A parsing, and chunking
│   ├── qdrant_setup.py         # Qdrant client, dense+sparse hybrid RRF search
│   ├── agent.py                # LLM Tool-Calling agent loop & guardrails
│   └── db/
│       ├── __init__.py         # DB package exports
│       ├── database.py         # SQLAlchemy engine & session manager
│       ├── models.py           # User, Conversation, ChatMessage, Ticket ORM models
│       ├── user.py             # User lookup & default user seeding
│       ├── convo.py            # Conversation & message repository
│       └── ticket.py           # Ticket creation and lookup repository
├── docker-compose.yml          # Docker composition for API, Qdrant & PostgreSQL
├── Dockerfile                  # API container Dockerfile
└── pyproject.toml              # Dependencies and project metadata
```

---

## 3. Core Design & Features

### 📄 PDF Data Extraction & Structured Q&A Indexing
- **PDF Input Only:** Strictly processes `.pdf` documents page by page.
- **Pattern-Aware Q&A Chunking:** Automatically detects structured Q&A indexing patterns (`1.`, `Question 1.`, `Q1.`, `a).`) in uploaded documents.
- **Cross-Page Cutoff Merging:** Unifies multi-page questions and answers so that split questions spanning page cutoffs stay intact in single chunks.

### 🔎 Native Server-Side Hybrid Search (`search_database`)
- **Dense Semantic Vector Search:** Computes cosine similarity over text embeddings (`gemini-embedding-2` / `text-embedding-3-small`) via named vector `"dense"`.
- **Sparse Keyword BM25 Search:** Utilizes `FastEmbed` (`Qdrant/bm25`) for native inverted sparse vectors via named vector `"sparse"`.
- **Qdrant Native Server-Side RRF:** Executes `models.FusionQuery(fusion=models.Fusion.RRF)` with `models.Prefetch` directly inside the Qdrant engine for maximum speed and zero Python RAM overhead.

### 🤖 LLM Tool Calling Agent (Exactly 2 Tools)
The agent operates via an iterative function execution loop using:
1. `search_database(query)`: Queries indexed document passages using Qdrant Native Server-Side RRF.
2. `create_issue_tickets(name, description)`: Creates an issue ticket directly in PostgreSQL with an auto-incrementing SQL primary key `id`.

### 🛡️ Anti-Hallucination Guardrails
- Strict system prompt rules enforce that all facts must be grounded in retrieved document chunks.
- Mandatory refusal fallback when information is missing:
  > `"I couldn't find this information in the provided documents."`

---

## 4. Quickstart & Installation

### Environment Setup (`uv`)
```bash
# Clone and enter project directory
cd rag_test

# Install dependencies using uv
uv sync

# Copy environment template
cp .env.example .env
```

Set your configuration in `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=gemini-embedding-2
DATABASE_URL=postgresql+psycopg2://rag_user:rag_pass123@localhost:5432/rag_db
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=documents
```

### Running Locally
```bash
# Apply database migrations
uv run alembic upgrade head

# Start FastAPI application
uv run uvicorn main:app --reload --port 8000
```
Interactive API Swagger Docs: `http://localhost:8000/docs`

### Running via Docker Compose
```bash
docker-compose up --build
```

---

## 5. API Endpoint Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/documents/upload` | Upload a PDF document for extraction, chunking, and hybrid indexing |
| `GET` | `/documents` | List all processed PDF documents and metadata |
| `GET` | `/documents/{document_id}` | Retrieve details for a specific document |
| `POST` | `/chat` | Submit question to LLM Agent (triggers `search_database` / `create_issue_tickets`) |
| `GET` | `/history` | Retrieve user chat conversation history |
| `POST` | `/tickets` | Directly create an issue ticket |
| `GET` | `/tickets` | List all created issue tickets |
| `GET` | `/health` | Health check and database connectivity status |

### Example Request & Response (`POST /chat`)

**Request:**
```json
{
  "question": "What is the annual leave allowance for full-time employees?"
}
```

**Response:**
```json
{
  "answer": "Full-time employees are entitled to 18 days of paid annual leave per calendar year.",
  "sources": [
    {
      "document": "sample_company_policy.pdf",
      "page": 1
    }
  ],
  "tool_calls": [
    {
      "function_name": "search_database",
      "function_args": {
        "query": "annual leave allowance full-time employees"
      }
    }
  ]
}
```

---

## 6. Evaluation Suite (`eval_suite.py`)

The codebase includes an evaluation suite testing **10 edge-case scenarios**:
1. **Direct Lookup:** Single-fact extraction.
2. **Direct Lookup (Secondary):** Metric lookup.
3. **Multi-Chunk / Cross-Page:** Synthesizing facts across multiple sections.
4. **Out-of-Domain / Unknowns:** Out-of-domain refusal check.
5. **Paraphrased / Semantic Shift:** Synonym and rephrased query handling.
6. **Adversarial / Distractor:** Visually/semantically misleading distractors.
7. **Tool Call - Issue Ticket:** Triggering `create_issue_tickets`.
8. **Tool Call - Bug Report:** Triggering bug logging.
9. **Out-of-Domain Refusal:** General trivia refusal.
10. **Multi-Page Synthesis:** Cross-page workflow explanation.

Run evaluation suite:
```bash
uv run python eval_suite.py
```
Output results are logged in `eval_results.json`.

---

## 7. Production Discussion Questions

### 1. Large Documents (500-Page Documents with Tables & Images)
- **Challenge:** Heavy memory footprint, layout context loss, and table parsing failure.
- **Solution:** 
  1. Use layout-aware PDF parsers (e.g. `pdfminer.six`, `Unstructured`, or `PyMuPDF` with layout parsing) to extract structural bounding boxes.
  2. Perform Table Extraction using specialized tools like `pdfplumber` or convert tables into Markdown/HTML string representations before chunking.
  3. Image/OCR Handling: Use Vision Models (e.g., GPT-4o vision or Tesseract OCR) to extract text embedded inside images/charts and index it as structured metadata.

### 2. Multi-Tenancy & Security Context Isolation
- **Challenge:** Preventing User A from retrieving User B's sensitive document chunks.
- **Solution:**
  1. Metadata Payload Filtering: Every chunk stored in the vector database includes tenant metadata (`tenant_id`, `user_id`, `workspace_id`).
  2. Mandatory Query Scoping: All vector queries forcefully apply a strict metadata filter: `WHERE tenant_id = current_user.tenant_id`.
  3. Vector Store Namespaces: Partition collections or namespaces per tenant in Qdrant or Pinecone.

### 3. Scale & Performance (10 to 10,000 Concurrent Users)
- **Challenge:** Latency bottlenecks, DB connection limits, and embedding rate limits.
- **Solution:**
  1. Asynchronous Ingestion Pipelines: Offload document processing to background worker queues (Celery / Redis / Kafka).
  2. Scalable Vector DB Indexing: Transition from in-memory stores to `pgvector` with HNSW indexes or distributed vector DBs (Qdrant/Milvus cluster).
  3. API Scaling & Caching: Deploy FastAPI instances behind a load balancer (Nginx/Envoy) and implement semantic caching (Redis / GPTCache) for frequent queries.

### 4. Embedding Cost & Deduplication
- **Challenge:** Redundant re-embedding of identical documents and repeated text chunks across versions.
- **Solution:**
  1. Content Hashing (SHA-256): Compute SHA-256 hash of document bytes and individual text chunks before calling embedding APIs. Skip embedding if chunk hash already exists in DB.
  2. Global Vector Cache: Maintain a cache mapping `hash(chunk_text) -> embedding_vector`.

### 5. Document Lifecycle (Updates, Soft Deletes, Versioning)
- **Challenge:** Stale chunks remaining in search indices when documents are modified or removed.
- **Solution:**
  1. Soft Delete & Tombstoning: Flag deleted documents with `is_deleted = true` in DB and filter them out during retrieval.
  2. Atomic Re-indexing: When a document version is updated, mark previous version chunks as archived and insert new version chunks under `version_id`.
  3. Garbage Collection: Run periodic background cron jobs to purge soft-deleted vector points from vector collections.

### 6. Retrieval Debugging ("Answer exists, but AI cannot find it")
- **Challenge:** Diagnosing retrieval failures in production RAG systems.
- **Solution:**
  1. RAG Triad Evaluation: Measure Context Relevance, Groundedness, and Answer Relevance using frameworks like Ragas or TruLens.
  2. Inspect Hybrid Weights: Analyze whether BM25 or Dense search failed. If query terms were exact, adjust BM25 weight; if semantic, check embedding distance.
  3. Re-ranking: Add a 2nd-stage Re-ranker (e.g., Cohere ReRank or BGE-Reranker) to re-order top-50 retrieved candidates down to top-4.

### 7. Irrelevant Retrieval Edge-Cases & Anti-Hallucination
- **Challenge:** Low-confidence or noisy retrieved chunks leading to hallucinated answers.
- **Solution:**
  1. Distance/Score Thresholding: Drop retrieved chunks whose similarity score falls below a strict minimum confidence threshold (e.g., cosine similarity < 0.70).
  2. System Prompt Guardrails: Explicit system instructions dictating that if no retrieved chunks meet confidence criteria, return the exact refusal response: `"I couldn't find this information in the provided documents."`
