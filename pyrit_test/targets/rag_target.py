"""
pyrit_test/targets/rag_target.py
================================
HTTPTarget builders and httpx client transport logic for POST /chat and POST /documents/upload.
"""

import time
import httpx
from pyrit.prompt_target import HTTPTarget
from pyrit_test.config import BASE_URL, HOST, SEND_SESSION_ID


def build_http_target(client: httpx.AsyncClient, session_id: str = None) -> HTTPTarget:
    """Build a PyRIT HTTPTarget pointing to the local RAG /chat endpoint."""
    body = '{"question": "{PROMPT}"'
    if SEND_SESSION_ID and session_id:
        body += f', "session_id": "{session_id}"'
    body += '}'

    http_req = (
        "POST /chat HTTP/1.1\n"
        f"Host: {HOST}\n"
        "Content-Type: application/json\n\n"
        + body
    )
    return HTTPTarget(http_request=http_req, use_tls=False, client=client)


async def chat_request(client: httpx.AsyncClient, question: str, session_id: str = None) -> dict:
    """Send a question to POST /chat with latency tracking and status checks."""
    payload = {"question": question}
    if SEND_SESSION_ID and session_id:
        payload["session_id"] = session_id

    t0 = time.perf_counter()
    empty = dict(answer="", sources=[], tool_calls=[])

    try:
        resp = await client.post(f"{BASE_URL}/chat", json=payload)
    except Exception as e:
        return dict(ok=False, status=None, error=f"{type(e).__name__}: {e}"[:200],
                    latency_ms=(time.perf_counter() - t0) * 1000, **empty)

    latency = (time.perf_counter() - t0) * 1000
    if resp.status_code != 200:
        return dict(ok=False, status=resp.status_code, error=resp.text[:200], latency_ms=latency, **empty)

    try:
        data = resp.json()
    except Exception:
        return dict(ok=False, status=200, error="response was not JSON", latency_ms=latency, **empty)

    return dict(ok=True, status=200, error="", latency_ms=latency,
                answer=str(data.get("answer", "")), sources=data.get("sources") or [],
                tool_calls=data.get("tool_calls") or [])


async def upload_pdf_document(client: httpx.AsyncClient, filename: str, pdf_bytes: bytes) -> dict:
    """Upload a PDF document to POST /documents/upload and parse document ID."""
    try:
        resp = await client.post(
            f"{BASE_URL}/documents/upload",
            files={"file": (filename, pdf_bytes, "application/pdf")}
        )
        if resp.status_code >= 400:
            quarantined = "Quarantine" in resp.text or resp.status_code == 400
            return dict(ok=False, status=resp.status_code, quarantined=quarantined, error=resp.text[:300])

        data = resp.json()
        doc_info = data.get("document") or data if isinstance(data, dict) else {}
        doc_id = doc_info.get("document_id") or doc_info.get("id") or data.get("document_id")
        return dict(ok=True, status=200, document_id=doc_id, total_chunks=doc_info.get("total_chunks", 1))
    except Exception as e:
        return dict(ok=False, status=None, quarantined=False, error=f"{type(e).__name__}: {e}"[:300])
