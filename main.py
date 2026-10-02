import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.models import (
    UploadResponse, DocumentMetadata,
    ChatRequest, ChatResponse,
    TicketRequest, TicketResponse,
    MessageHistory,
)
from src.pdf_processor import process_pdf_document, detect_hidden_spans
from src.qdrant_setup import qdrant
from src.agent import run_agent_chat
from src.db import (
    get_db,
    seed_default_user,
    resolve_user,
    get_or_create_user,
    get_or_create_single_conversation,
    save_message,
    load_chat_history,
    get_all_messages,
    clear_chat_history,
    execute_create_issue_ticket,
    get_all_tickets,
)
from src.db.database import check_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with get_db() as db:
            seed_default_user(db)
    except Exception as e:
        print(f"no default user: {e}")
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    db_ok = check_connection()
    return {"status": "ok", "db_connected": db_ok}

@app.post("/documents/upload",response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="only pdf files are supported.")
    try:
        file_content = await file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        
        # Quarantine PDFs containing steganographic/hidden text spans
        hidden_spans = detect_hidden_spans(file_content)
        if hidden_spans:
            raise HTTPException(
                status_code=400,
                detail=f"Security Quarantine: PDF contains hidden/steganographic text spans ({len(hidden_spans)} detected)."
            )

        document_id = f"doc_{uuid.uuid4().hex[:10]}"
        processed_doc = process_pdf_document(file_content, file.filename, document_id)
        doc_metadata = qdrant.add_document(processed_doc)

        return UploadResponse(message="document successfully added.",document=DocumentMetadata(**doc_metadata))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to upload document: {str(e)}")


@app.get("/documents", response_model=List[DocumentMetadata])
def list_documents():
    return [DocumentMetadata(**doc) for doc in qdrant.list_documents()]


@app.get("/documents/{document_id}", response_model=DocumentMetadata)
def get_document(document_id: str):
    doc = qdrant.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"document not found.")
    return DocumentMetadata(**doc)


@app.delete("/documents/{document_id}")
def delete_document(document_id: str):
    success = qdrant.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"document not found.")
    return {"message": "document successfully deleted."}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="query cannot be empty")

    if len(request.question) > 10000:
        raise HTTPException(status_code=400, detail="Query length exceeds maximum limit of 10000 characters.")

    query_received_at = datetime.now(timezone.utc)
    # Generate fresh session UUID if none provided to prevent shared default bucket leaks
    effective_session_id = request.session_id or request.user_id or uuid.uuid4().hex

    chat_history = []
    conversation = None
    try:
        with get_db() as db:
            user = resolve_user(db, request.user_id)
            conversation = get_or_create_single_conversation(db, user, session_id=effective_session_id)
            chat_history = load_chat_history(db, conversation, limit=10)
    except Exception as e:
        print(f"failed to load old chat:{e}")

    try:
        answer, sources, tool_calls = run_agent_chat(
            question=request.question,
            chat_history=chat_history,
        )
        response_status = "success"
        error_detail = None
    except Exception as error:
        answer = "encountered an error processing"
        sources = []
        tool_calls = []
        response_status = "error"
        error_detail = str(error)

    response_sent_at = datetime.now(timezone.utc)
    message_id = "unknown"
    processing_ms = None
    try:
        with get_db() as db:
            user = resolve_user(db, request.user_id)
            conv = get_or_create_single_conversation(db, user, session_id=effective_session_id)
            saved_message = save_message(
                db=db,
                conversation=conv,
                user_query=request.question,
                query_received_at=query_received_at,
                assistant_reply=answer,
                response_sent_at=response_sent_at,
                citations=sources,
                tool_calls=tool_calls,
                status=response_status,
                error_detail=error_detail,
            )
            message_id = str(saved_message.id)
            processing_ms = saved_message.processing_time_ms
    except Exception as db_error:
        print(f"message save failed:{db_error}")

    return ChatResponse(
        answer=answer,
        sources=sources,
        tool_calls=tool_calls,
        message_id=message_id,
        processing_time_ms=processing_ms,
    )


# --- Chat History ---

@app.get("/history", response_model=List[MessageHistory], tags=["History"])
def get_chat_history(user_id: Optional[str] = Query(default=None),limit: int = Query(default=20, ge=1, le=200)):
    try:
        with get_db() as db:
            user = resolve_user(db, user_id)
            conv = get_or_create_single_conversation(db, user)
            all_messages = get_all_messages(db, conv)

            # Only return the last N messages
            recent_messages = all_messages[-limit:]

            history = []
            for message in recent_messages:
                history.append(MessageHistory(
                    message_id=str(message.id),
                    user_id=str(user.id),
                    user_query=message.user_query,
                    assistant_reply=message.assistant_reply,
                    citations=message.citations or [],
                    ticket_id=message.ticket_id,
                    ticket_created=message.ticket_created or False,
                    processing_time_ms=message.processing_time_ms,
                    status=message.status or "success",
                    query_received_at=message.query_received_at,
                    response_sent_at=message.response_sent_at,
                ))

            return history
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Failed to load history: {str(error)}")


@app.delete("/history", tags=["History"])
def delete_chat_history(user_id: Optional[str] = Query(default=None)):
    try:
        with get_db() as db:
            user = resolve_user(db, user_id)
            conv = get_or_create_single_conversation(db, user)
            clear_chat_history(db, conv)
            db.commit()
            return {"message": "chat history successfully deleted."}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Failed to delete history: {str(error)}")


# --- Tickets ---

@app.post("/tickets", response_model=TicketResponse, tags=["Tickets"])
def create_ticket(request: TicketRequest):
    ticket_data = execute_create_issue_ticket(name=request.name,description=request.description)
    return TicketResponse(**ticket_data)


@app.get("/tickets", response_model=List[TicketResponse], tags=["Tickets"])
def list_tickets():
    """Get all tickets."""
    with get_db() as db:
        tickets = get_all_tickets(db)
        result = []
        for ticket in tickets:
            result.append(TicketResponse(
                id=ticket.id,
                name=ticket.name,
                description=ticket.description,
                status=ticket.status,
                created_at=ticket.created_at.isoformat() if ticket.created_at else "",
            ))
        return result
