from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from src.db.models import Ticket
from src.db.database import get_db


def create_ticket(db: Session, name: str, description: str):
    ticket = Ticket(name=name, description=description)
    db.add(ticket)
    db.flush()
    return ticket


def get_all_tickets(db: Session):
    return db.query(Ticket).order_by(Ticket.id.asc()).all()


def get_ticket_by_id(db: Session, ticket_id: int):
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def execute_create_issue_ticket(name: str, description: str):
    with get_db() as db:
        ticket = create_ticket(db, name=name, description=description)
        return {
            "id": ticket.id,
            "name": ticket.name,
            "description": ticket.description,
            "status": ticket.status,
            "created_at": ticket.created_at.isoformat(),
        }
