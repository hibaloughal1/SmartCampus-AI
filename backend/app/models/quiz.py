import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR

from app.database.session import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(CHAR(36), primary_key=True, default=gen_uuid)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    document_id = Column(CHAR(36), ForeignKey("documents.id"), nullable=True)
    title = Column(String(255), nullable=False)
    topic = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(CHAR(36), primary_key=True, default=gen_uuid)
    quiz_id = Column(CHAR(36), ForeignKey("quizzes.id"), nullable=False)
    question = Column(Text, nullable=False)
    option_a = Column(String(500), nullable=False)
    option_b = Column(String(500), nullable=False)
    option_c = Column(String(500), nullable=False)
    option_d = Column(String(500), nullable=False)
    correct_option = Column(String(1), nullable=False)  # 'A' | 'B' | 'C' | 'D'
    explanation = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)

    quiz = relationship("Quiz", back_populates="questions")
