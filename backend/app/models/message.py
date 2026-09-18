import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR

from app.database.session import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"


class Message(Base):
    __tablename__ = "messages"

    id = Column(CHAR(36), primary_key=True, default=gen_uuid)
    conversation_id = Column(CHAR(36), ForeignKey("conversations.id"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    sources = Column(Text, nullable=True)  # JSON-encoded list of {document, chunk, score}
    response_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
