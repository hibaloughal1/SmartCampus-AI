from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.quiz import (
    QuizGenerateRequest, QuizOut, FlashcardGenerateRequest, FlashcardSetOut,
)
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.quiz import Quiz
from app.models.flashcard import FlashcardSet
from app.services.quiz_service import create_quiz, create_flashcard_set

router = APIRouter(prefix="/api", tags=["Quiz et Flashcards"])


@router.post("/quiz/generate", response_model=QuizOut)
async def generate_quiz(payload: QuizGenerateRequest, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    return await create_quiz(db, current_user.id, payload.document_id, payload.topic, payload.num_questions)


@router.get("/quiz", response_model=List[QuizOut])
def list_quizzes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Quiz).filter(Quiz.user_id == current_user.id).order_by(Quiz.created_at.desc()).all()


@router.get("/quiz/{quiz_id}", response_model=QuizOut)
def get_quiz(quiz_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()


@router.post("/flashcards/generate", response_model=FlashcardSetOut)
async def generate_flashcards(payload: FlashcardGenerateRequest, db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    return await create_flashcard_set(db, current_user.id, payload.document_id, payload.topic, payload.num_cards)


@router.get("/flashcards", response_model=List[FlashcardSetOut])
def list_flashcard_sets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(FlashcardSet)
        .filter(FlashcardSet.user_id == current_user.id)
        .order_by(FlashcardSet.created_at.desc())
        .all()
    )


@router.get("/flashcards/{set_id}", response_model=FlashcardSetOut)
def get_flashcard_set(set_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(FlashcardSet)
        .filter(FlashcardSet.id == set_id, FlashcardSet.user_id == current_user.id)
        .first()
    )
