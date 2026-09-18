from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.document import Document
from app.models.message import Message, MessageRole
from app.models.department import Subject


def get_dashboard_stats(db: Session) -> dict:
    num_users = db.query(func.count(User.id)).scalar() or 0
    num_documents = db.query(func.count(Document.id)).scalar() or 0
    num_questions = db.query(func.count(Message.id)).filter(Message.role == MessageRole.USER).scalar() or 0

    avg_response_time = (
        db.query(func.avg(Message.response_time_ms))
        .filter(Message.role == MessageRole.ASSISTANT, Message.response_time_ms.isnot(None))
        .scalar()
    ) or 0.0

    most_viewed = (
        db.query(Document.title, Document.num_views)
        .order_by(Document.num_views.desc())
        .limit(5)
        .all()
    )

    most_used_subjects = (
        db.query(Subject.name, func.count(Document.id).label("cnt"))
        .join(Document, Document.subject_id == Subject.id)
        .group_by(Subject.name)
        .order_by(func.count(Document.id).desc())
        .limit(5)
        .all()
    )

    return {
        "num_users": num_users,
        "num_documents": num_documents,
        "num_questions": num_questions,
        "avg_response_time_ms": round(float(avg_response_time), 2),
        "most_viewed_documents": [{"title": t, "views": v} for t, v in most_viewed],
        "most_used_subjects": [{"name": n, "count": c} for n, c in most_used_subjects],
    }
