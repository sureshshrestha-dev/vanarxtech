from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class SourceAttribution(BaseModel):
    document: str
    page: int


class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    total_pages: int
    total_chunks: int
    created_at: str


class UploadResponse(BaseModel):
    message: str
    document: DocumentMetadata


class ChatRequest(BaseModel):
    question: str
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceAttribution] = []
    tool_calls: List[Dict[str, Any]] = []
    message_id: str
    processing_time_ms: Optional[float] = None


class MessageHistory(BaseModel):
    message_id: str
    user_id: Optional[str] = None
    user_query: str
    assistant_reply: Optional[str] = None
    citations: List[Dict[str, Any]] = []
    ticket_id: Optional[str] = None
    ticket_created: bool = False
    processing_time_ms: Optional[float] = None
    status: str
    query_received_at: datetime
    response_sent_at: Optional[datetime] = None


class TicketRequest(BaseModel):
    name: str
    description: str


class TicketResponse(BaseModel):
    id: int
    name: str
    description: str
    status: str
    created_at: str
