from typing import List, Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.document import DocumentOut, DocumentUpdate
from app.auth.dependencies import require_admin, get_current_user
from app.models.user import User
from app.models.document import Document
from app.services.document_service import (
    save_uploaded_file, create_document_record, process_document, delete_document,
)
from app.rag.document_processor import DocumentProcessor

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    subject_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if not DocumentProcessor.is_supported(file.filename):
        raise HTTPException(status_code=400, detail="Format non supporté. Utilisez PDF, DOCX, PPTX ou TXT.")

    file_path = await save_uploaded_file(file)
    document = create_document_record(
        db, title=title or file.filename, filename=file.filename,
        file_path=file_path, subject_id=subject_id, uploaded_by_id=current_user.id,
    )
    # Ingestion pipeline runs in the background so the upload responds immediately.
    background_tasks.add_task(process_document, db, document)
    return document


@router.get("", response_model=List[DocumentOut])
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Document).order_by(Document.created_at.desc()).all()


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document introuvable")
    document.num_views += 1
    db.commit()
    return document


@router.put("/{document_id}", response_model=DocumentOut)
def update_document(document_id: str, payload: DocumentUpdate, db: Session = Depends(get_db),
                     current_user: User = Depends(require_admin)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document introuvable")
    if payload.title is not None:
        document.title = payload.title
    if payload.subject_id is not None:
        document.subject_id = payload.subject_id
    db.commit()
    db.refresh(document)
    return document


@router.delete("/{document_id}", status_code=204)
def remove_document(document_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document introuvable")
    delete_document(db, document)
