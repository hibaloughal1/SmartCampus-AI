from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models.document import DocumentStatus, DocumentType


class DocumentOut(BaseModel):
    id: str
    title: str
    filename: str
    file_type: DocumentType
    status: DocumentStatus
    num_chunks: int
    num_views: int
    subject_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    subject_id: Optional[str] = None
