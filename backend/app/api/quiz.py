from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.quiz import (
    QuizGenerateRequest, QuizOut, FlashcardGenerateRequest, FlashcardSetOut
)
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.quiz import Quiz
from app.models.flashcard import FlashcardSet
from app.services.quiz_service import generate_quiz, generate_flashcards
from typing import List
from fastapi import HTTPException, status

router = APIRouter(prefix="/api", tags=["Quiz & Flashcards"])


@router.post("/quiz/generate", response_model=QuizOut)
async def create_quiz(payload: QuizGenerateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await generate_quiz(db, current_user.id, payload.document_id, payload.topic, payload.num_questions)


@router.get("/quiz", response_model=List[QuizOut])
def list_quizzes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Quiz).filter(Quiz.user_id == current_user.id).order_by(Quiz.created_at.desc()).all()


@router.get("/quiz/{quiz_id}", response_model=QuizOut)
def get_quiz(quiz_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz introuvable")
    return quiz


@router.post("/flashcards/generate", response_model=FlashcardSetOut)
async def create_flashcards(payload: FlashcardGenerateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await generate_flashcards(db, current_user.id, payload.document_id, payload.topic, payload.num_cards)


@router.get("/flashcards", response_model=List[FlashcardSetOut])
def list_flashcard_sets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(FlashcardSet).filter(FlashcardSet.user_id == current_user.id).order_by(FlashcardSet.created_at.desc()).all()


@router.get("/flashcards/{set_id}", response_model=FlashcardSetOut)
def get_flashcard_set(set_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    fset = db.query(FlashcardSet).filter(FlashcardSet.id == set_id, FlashcardSet.user_id == current_user.id).first()
    if not fset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ensemble de flashcards introuvable")
    return fset
