"""
Conversational memory: retrieves the last N messages of a conversation to
give the LLM short-term context (section 5.15 of the cahier des charges).
"""
from typing import List

from sqlalchemy.orm import Session

from app.config import settings
from app.models.message import Message


def get_recent_history(db: Session, conversation_id: str) -> List[dict]:
    limit = settings.CONVERSATION_MEMORY_SIZE
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )
    messages.reverse()
    return [{"role": m.role.value, "content": m.content} for m in messages]
