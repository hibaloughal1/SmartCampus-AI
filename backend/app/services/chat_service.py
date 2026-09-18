import json

from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.rag.rag_engine import answer_question


async def ask_question(db: Session, user_id: str, question: str, conversation_id: str = None):
    if conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id, Conversation.user_id == user_id
        ).first()
        if not conversation:
            conversation = Conversation(user_id=user_id, title=question[:60])
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
    else:
        conversation = Conversation(user_id=user_id, title=question[:60])
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    user_message = Message(conversation_id=conversation.id, role=MessageRole.USER, content=question)
    db.add(user_message)
    db.commit()

    rag_response = await answer_question(db, question, conversation.id)

    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=rag_response.answer,
        sources=json.dumps(rag_response.sources, ensure_ascii=False),
        response_time_ms=rag_response.response_time_ms,
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    return conversation, rag_response
