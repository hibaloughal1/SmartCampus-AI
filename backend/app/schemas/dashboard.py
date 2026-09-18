from typing import List
from pydantic import BaseModel


class DocumentStat(BaseModel):
    title: str
    views: int


class SubjectStat(BaseModel):
    name: str
    count: int


class DashboardStats(BaseModel):
    num_users: int
    num_documents: int
    num_questions: int
    avg_response_time_ms: float
    most_viewed_documents: List[DocumentStat]
    most_used_subjects: List[SubjectStat]
