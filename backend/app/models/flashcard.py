import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR

from app.database.session import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class FlashcardSet(Base):
    __tablename__ = "flashcard_sets"

    id = Column(CHAR(36), primary_key=True, default=gen_uuid)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    document_id = Column(CHAR(36), ForeignKey("documents.id"), nullable=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="flashcard_sets")
    flashcards = relationship("Flashcard", back_populates="flashcard_set", cascade="all, delete-orphan")


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(CHAR(36), primary_key=True, default=gen_uuid)
    flashcard_set_id = Column(CHAR(36), ForeignKey("flashcard_sets.id"), nullable=False)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    order_index = Column(Integer, default=0)

    flashcard_set = relationship("FlashcardSet", back_populates="flashcards")
