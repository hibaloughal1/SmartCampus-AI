from typing import List, Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.document import DocumentOut, DocumentUpdate
from app.auth.dependencies import get_current_user, require_admin
from app.models.user import User
from app.models.document import Document
from app.services.document_service import create_document_record, process_document, delete_document

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("", response_model=DocumentOut, status_code=201)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    subject_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    document = create_document_record(db, file, title, subject_id, admin.id)
    background_tasks.add_task(_process_in_background, document.id)
    return document


def _process_in_background(document_id: str):
    from app.database.session import SessionLocal
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            process_document(db, document)
    finally:
        db.close()


@router.get("", response_model=List[DocumentOut])
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Document).order_by(Document.created_at.desc()).all()


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable")
    document.num_views = (document.num_views or 0) + 1
    db.commit()
    db.refresh(document)
    return document


@router.patch("/{document_id}", response_model=DocumentOut)
def update_document(document_id: str, payload: DocumentUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable")
    if payload.title is not None:
        document.title = payload.title
    if payload.subject_id is not None:
        document.subject_id = payload.subject_id
    db.commit()
    db.refresh(document)
    return document


@router.delete("/{document_id}", status_code=204)
def remove_document(document_id: str, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable")
    delete_document(db, document)
    return None


@router.post("/{document_id}/reprocess", response_model=DocumentOut)
def reprocess_document(document_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable")
    background_tasks.add_task(_process_in_background, document.id)
    return document
