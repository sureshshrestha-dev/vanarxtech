import uuid
from sqlalchemy.orm import Session
from src.db.models import User, Conversation


# Default user settings (used when no user_id is provided in API requests)
DEFAULT_USER = {
    "id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
    "name": "rag_user",
    "email": "user@ragtest.local",
    "is_default": True,
}


def seed_default_user(db: Session):
    user = db.query(User).filter(User.id == DEFAULT_USER["id"]).first()

    if not user:
        user = User(**DEFAULT_USER)
        db.add(user)
        db.flush()
        print(f"[User] Created default user: {user.name} ({user.email})")

    return user


def get_default_user(db: Session):
    user = db.query(User).filter(User.is_default == True).first()
    if not user:
        user = seed_default_user(db)
    return user


def get_user_by_id(db: Session, user_id: uuid.UUID):
    return db.query(User).filter(User.id == user_id).first()


def resolve_user(db: Session, user_id: str = None):
    if user_id:
        try:
            user = get_user_by_id(db, uuid.UUID(user_id))
            if user:
                return user
        except (ValueError, Exception):
            pass

    return get_default_user(db)
