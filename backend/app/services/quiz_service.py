from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.models.quiz import Quiz, QuizQuestion
from app.models.flashcard import FlashcardSet, Flashcard
from app.rag.rag_engine import generate_quiz_json, generate_flashcards_json


def _get_context_text(db: Session, document_id: str = None, topic: str = None, max_chars: int = 4000) -> str:
    query = db.query(Chunk)
    if document_id:
        query = query.filter(Chunk.document_id == document_id)
    chunks = query.limit(20).all()
    text = "\n".join(c.content for c in chunks)
    return text[:max_chars]


async def create_quiz(db: Session, user_id: str, document_id: str, topic: str, num_questions: int) -> Quiz:
    context_text = _get_context_text(db, document_id, topic)
    if not context_text.strip():
        context_text = topic or "Cours général"

    questions_data = await generate_quiz_json(context_text, num_questions)

    document = db.query(Document).filter(Document.id == document_id).first() if document_id else None
    quiz = Quiz(
        user_id=user_id,
        document_id=document_id,
        title=f"Quiz - {document.title if document else (topic or 'Général')}",
        topic=topic,
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    for idx, q in enumerate(questions_data):
        try:
            question = QuizQuestion(
                quiz_id=quiz.id,
                question=q.get("question", ""),
                option_a=q.get("option_a", ""),
                option_b=q.get("option_b", ""),
                option_c=q.get("option_c", ""),
                option_d=q.get("option_d", ""),
                correct_option=str(q.get("correct_option", "A")).upper()[:1],
                explanation=q.get("explanation"),
                order_index=idx,
            )
            db.add(question)
        except Exception:
            continue
    db.commit()
    db.refresh(quiz)
    return quiz


async def create_flashcard_set(db: Session, user_id: str, document_id: str, topic: str, num_cards: int) -> FlashcardSet:
    context_text = _get_context_text(db, document_id, topic)
    if not context_text.strip():
        context_text = topic or "Cours général"

    cards_data = await generate_flashcards_json(context_text, num_cards)

    document = db.query(Document).filter(Document.id == document_id).first() if document_id else None
    fset = FlashcardSet(
        user_id=user_id,
        document_id=document_id,
        title=f"Flashcards - {document.title if document else (topic or 'Général')}",
    )
    db.add(fset)
    db.commit()
    db.refresh(fset)

    for idx, c in enumerate(cards_data):
        try:
            card = Flashcard(
                flashcard_set_id=fset.id,
                front=c.get("front", ""),
                back=c.get("back", ""),
                order_index=idx,
            )
            db.add(card)
        except Exception:
            continue
    db.commit()
    db.refresh(fset)
    return fset
