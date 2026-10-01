"""
Database package - exports everything other files need from the db layer.
Import from here instead of importing from individual db files.
"""
from src.db.models import Base
from src.db.database import SessionLocal, engine, get_db
from src.db.user import (
    DEFAULT_USER,
    seed_default_user,
    get_default_user,
    resolve_user,
)
from src.db.convo import (
    get_or_create_user,
    get_or_create_single_conversation,
    save_message,
    load_chat_history,
    get_all_messages,
    clear_chat_history,
    DEFAULT_USER_ID,
    DEFAULT_USER_NAME,
    DEFAULT_USER_EMAIL,
)
from src.db.ticket import (
    create_ticket,
    get_all_tickets,
    get_ticket_by_id,
    execute_create_issue_ticket,
)

__all__ = [
    # Database setup
    "Base",
    "SessionLocal",
    "engine",
    "get_db",
    # User management
    "seed_default_user",
    "get_default_user",
    "resolve_user",
    "DEFAULT_USER",
    "get_or_create_user",
    "DEFAULT_USER_ID",
    "DEFAULT_USER_NAME",
    "DEFAULT_USER_EMAIL",
    # Conversation and messages
    "get_or_create_single_conversation",
    "save_message",
    "load_chat_history",
    "get_all_messages",
    "clear_chat_history",
    # Tickets
    "create_ticket",
    "get_all_tickets",
    "get_ticket_by_id",
    "execute_create_issue_ticket",
]
