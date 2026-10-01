import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.db.models import User, Conversation, ChatMessage
from src.db.user import DEFAULT_USER, seed_default_user, get_default_user, resolve_user

DEFAULT_USER_NAME = DEFAULT_USER["name"]
DEFAULT_USER_EMAIL = DEFAULT_USER["email"]
DEFAULT_USER_ID = DEFAULT_USER["id"]


def get_or_create_user(db: Session, user_id: Optional[str] = None):
    return resolve_user(db, user_id)


def get_or_create_single_conversation(db: Session, user: User):
    conversation = db.query(Conversation).filter(Conversation.user_id == user.id).first()

    if not conversation:
        conversation = Conversation(user_id=user.id)
        db.add(conversation)
        db.flush()

    return conversation


def save_message(
    db: Session,
    conversation: Conversation,
    user_query: str,
    query_received_at: datetime,
    assistant_reply: str,
    response_sent_at: datetime,
    citations: List[Any],
    tool_calls: Optional[List[Dict[str, Any]]] = None,
    status: str = "success",
    error_detail: Optional[str] = None,
):
    processing_ms = None
    if response_sent_at and query_received_at:
        time_diff = response_sent_at - query_received_at
        processing_ms = time_diff.total_seconds() * 1000

    ticket_id = None
    ticket_created = False
    if tool_calls:
        for tool_call in tool_calls:
            if tool_call.get("function_name") == "create_issue_tickets":
                ticket_info = tool_call.get("result", {}).get("ticket", {})
                ticket_id = str(ticket_info.get("id") or ticket_info.get("ticket_id") or "")

    formatted_citations = []
    if citations:
        for source in citations:
            if hasattr(source, "document"):
                formatted_citations.append({
                    "document": source.document,
                    "page": source.page,
                })
            else:
                formatted_citations.append({
                    "document": source.get("document", ""),
                    "page": source.get("page", 0),
                })

    message = ChatMessage(
        conversation_id=conversation.id,
        user_query=user_query,
        query_received_at=query_received_at,
        assistant_reply=assistant_reply,
        response_sent_at=response_sent_at,
        processing_time_ms=processing_ms,
        citations=formatted_citations,
        tool_calls=None,
        ticket_id=ticket_id,
        ticket_created=ticket_created,
        status=status,
        error_detail=error_detail,
    )

    db.add(message)
    db.flush()
    return message


def load_chat_history(db: Session, conversation: Conversation, limit: int = 10):

    recent_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation.id)
        .order_by(ChatMessage.query_received_at.desc())
        .limit(limit)
        .all()
    )
    recent_messages.reverse()

    history = []
    for message in recent_messages:
        history.append({"role": "user", "content": message.user_query})
        history.append({"role": "assistant", "content": message.assistant_reply or ""})

    return history


def get_all_messages(db: Session, conversation: Conversation):
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation.id)
        .order_by(ChatMessage.query_received_at.asc())
        .all()
    )


def clear_chat_history(db: Session, conversation: Conversation):
    db.query(ChatMessage).filter(ChatMessage.conversation_id == conversation.id).delete()
    db.flush()
