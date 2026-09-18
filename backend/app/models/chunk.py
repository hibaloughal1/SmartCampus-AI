import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR

from app.database.session import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Chunk(Base):
    """A text segment produced by chunking a Document, with a pointer to its
    vector index position in the FAISS store (faiss_index)."""
    __tablename__ = "chunks"

    id = Column(CHAR(36), primary_key=True, default=gen_uuid)
    document_id = Column(CHAR(36), ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    faiss_index = Column(Integer, nullable=True)  # position in the FAISS vector store
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")
