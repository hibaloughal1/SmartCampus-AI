from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class SourceOut(BaseModel):
    document_id: str
    document_title: str
    chunk_content: str
    score: float


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    sources: List[SourceOut] = []
    response_time_ms: float


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    sources: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationDetailOut(ConversationOut):
    messages: List[MessageOut] = []
