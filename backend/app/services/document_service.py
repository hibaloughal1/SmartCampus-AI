"""
Handles the full document ingestion pipeline (section 3.3.3 of the cahier
des charges): save file -> extract text -> clean -> chunk -> embed ->
index in FAISS -> persist Chunk rows -> rebuild BM25 index.
"""
import os
import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.document import Document, DocumentStatus, DocumentType
from app.models.chunk import Chunk
from app.rag.document_processor import DocumentProcessor
from app.rag.chunking import chunk_text
from app.rag.embeddings import embed_texts
from app.rag.vector_store import get_vector_store
from app.rag import bm25_index

EXTENSION_TO_TYPE = {
    ".pdf": DocumentType.PDF,
    ".docx": DocumentType.DOCX,
    ".pptx": DocumentType.PPTX,
    ".txt": DocumentType.TXT,
}


def _document_type_from_filename(filename: str) -> DocumentType:
    suffix = Path(filename).suffix.lower()
    if suffix not in EXTENSION_TO_TYPE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Format non supporté : {suffix}")
    return EXTENSION_TO_TYPE[suffix]


async def save_uploaded_file(file: UploadFile) -> str:
    os.makedirs(settings.DOCUMENTS_PATH, exist_ok=True)
    safe_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(settings.DOCUMENTS_PATH, safe_name)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path


def create_document_record(db: Session, title: str, filename: str, file_path: str,
                            subject_id: str, uploaded_by_id: str) -> Document:
    doc = Document(
        title=title,
        filename=filename,
        file_path=file_path,
        file_type=_document_type_from_filename(filename),
        status=DocumentStatus.PENDING,
        subject_id=subject_id,
        uploaded_by_id=uploaded_by_id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def process_document(db: Session, document: Document):
    """Runs the ingestion pipeline synchronously. In production this would be
    offloaded to a background worker/task queue."""
    try:
        document.status = DocumentStatus.PROCESSING
        db.commit()

        raw_text = DocumentProcessor.extract_text(document.file_path)
        clean_text = DocumentProcessor.clean_text(raw_text)

        if not clean_text.strip():
            raise ValueError("Aucun texte n'a pu être extrait du document")

        chunks = chunk_text(clean_text)
        if not chunks:
            raise ValueError("Le découpage en segments n'a produit aucun chunk")

        embeddings = embed_texts(chunks)

        chunk_rows = []
        for idx, content in enumerate(chunks):
            chunk = Chunk(document_id=document.id, content=content, chunk_index=idx)
            db.add(chunk)
            chunk_rows.append(chunk)
        db.commit()
        for c in chunk_rows:
            db.refresh(c)

        metadata = [{"chunk_id": c.id, "document_id": document.id} for c in chunk_rows]
        faiss_positions = get_vector_store().add(embeddings, metadata)

        for chunk, pos in zip(chunk_rows, faiss_positions):
            chunk.faiss_index = pos
        db.commit()

        document.status = DocumentStatus.INDEXED
        document.num_chunks = len(chunks)
        db.commit()

        rebuild_bm25_index(db)

    except Exception as e:
        document.status = DocumentStatus.FAILED
        document.error_message = str(e)
        db.commit()
        raise


def rebuild_bm25_index(db: Session):
    """Rebuilds the in-memory BM25 lexical index from all chunks currently
    in the database (called after ingesting or deleting a document)."""
    rows = db.query(Chunk.id, Chunk.content).all()
    bm25_index.build_index([(cid, content) for cid, content in rows])


def delete_document(db: Session, document: Document):
    get_vector_store().remove_document(document.id)
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    db.delete(document)
    db.commit()
    rebuild_bm25_index(db)
