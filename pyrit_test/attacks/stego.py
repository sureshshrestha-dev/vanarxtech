"""
pyrit_test/attacks/stego.py
============================
PDF Steganography (white-text, micro-font, off-page) test suite runner.
"""

import uuid
import httpx
from typing import Dict, Any, List
from pyrit_test.config import CANARY_STEGO, DELETE_PATH, BASE_URL
from pyrit_test.targets.rag_target import chat_request, upload_pdf_document
from pyrit_test.scorers.canary_scorer import score_response, chunk_retrieved
from pyrit_test.utils.pdf_stego_gen import make_stego_pdf, STEGO_KINDS


async def run_stego_suite(client: httpx.AsyncClient, runs_count: int) -> List[Dict[str, Any]]:
    """Generate, upload, test, and clean up PDF steganography attack probes."""
    records = []
    uploaded_ids = []

    for kind in STEGO_KINDS:
        filename, pdf_bytes, queries = make_stego_pdf(kind)
        up = await upload_pdf_document(client, filename, pdf_bytes)

        # Ingestion Quarantine check
        if not up.get("ok"):
            if up.get("quarantined"):
                for q in queries:
                    for r in range(runs_count):
                        base_record = dict(
                            suite="pdf_stego", category=f"Hidden text: {kind}", variant="plaintext",
                            run=r, prompt=q, sent=q, planted=CANARY_STEGO
                        )
                        records.append({
                            **base_record, "answer": "", "sources": [], "tool_calls": [],
                            "status": up["status"], "latency_ms": 0, "retrieved": False,
                            "passed": True, "detail": "quarantined at ingestion pipeline",
                            "document_id": None
                        })
            else:
                print(f"  ! upload error for {kind}: HTTP {up.get('status')} - {up.get('error')}")
            continue

        doc_id = up.get("document_id")
        if doc_id:
            uploaded_ids.append(doc_id)

        for q in queries:
            for r in range(runs_count):
                base_record = dict(
                    suite="pdf_stego", category=f"Hidden text: {kind}", variant="plaintext",
                    run=r, prompt=q, sent=q, planted=CANARY_STEGO
                )
                chat_res = await chat_request(client, q, uuid.uuid4().hex)
                if not chat_res["ok"]:
                    records.append({
                        **base_record, "answer": "", "sources": [], "tool_calls": [],
                        "status": chat_res["status"], "latency_ms": round(chat_res["latency_ms"]),
                        "retrieved": None, "passed": None, "detail": f"error: HTTP {chat_res['status']} {chat_res['error']}",
                        "document_id": doc_id
                    })
                    continue

                passed, detail = score_response("indirect_injection", [CANARY_STEGO], chat_res)
                retrieved = chunk_retrieved(chat_res, CANARY_STEGO)
                if retrieved and passed:
                    detail = "hidden text INGESTED and retrieved, but not obeyed"

                records.append({
                    **base_record,
                    "answer": chat_res["answer"],
                    "sources": chat_res["sources"],
                    "tool_calls": chat_res["tool_calls"],
                    "status": chat_res["status"],
                    "latency_ms": round(chat_res["latency_ms"]),
                    "retrieved": retrieved,
                    "passed": passed,
                    "detail": detail,
                    "document_id": doc_id,
                    "total_chunks": up.get("total_chunks", 1)
                })

    # Auto-cleanup uploaded test PDFs
    for doc_id in uploaded_ids:
        if DELETE_PATH and doc_id:
            try:
                del_resp = await client.delete(f"{BASE_URL}{DELETE_PATH.format(document_id=doc_id)}")
                print(f"  cleanup: DELETE {doc_id} -> HTTP {del_resp.status_code}")
            except Exception as e:
                print(f"  cleanup failed for {doc_id}: {e}")

    return records
