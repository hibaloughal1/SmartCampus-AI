import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR

from app.database.session import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class DocumentType(str, enum.Enum):
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    TXT = "txt"


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(CHAR(36), primary_key=True, default=gen_uuid)
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(Enum(DocumentType), nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    subject_id = Column(CHAR(36), ForeignKey("subjects.id"), nullable=True)
    uploaded_by_id = Column(CHAR(36), ForeignKey("users.id"), nullable=True)
    num_chunks = Column(Integer, default=0)
    num_views = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subject = relationship("Subject", back_populates="documents")
    uploaded_by = relationship("User", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
