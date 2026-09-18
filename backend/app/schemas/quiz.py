from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class QuizGenerateRequest(BaseModel):
    document_id: Optional[str] = None
    topic: Optional[str] = None
    num_questions: int = 5


class QuizQuestionOut(BaseModel):
    id: str
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str
    explanation: Optional[str] = None

    class Config:
        from_attributes = True


class QuizOut(BaseModel):
    id: str
    title: str
    topic: Optional[str] = None
    created_at: datetime
    questions: List[QuizQuestionOut] = []

    class Config:
        from_attributes = True


class FlashcardGenerateRequest(BaseModel):
    document_id: Optional[str] = None
    topic: Optional[str] = None
    num_cards: int = 10


class FlashcardOut(BaseModel):
    id: str
    front: str
    back: str

    class Config:
        from_attributes = True


class FlashcardSetOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    flashcards: List[FlashcardOut] = []

    class Config:
        from_attributes = True
