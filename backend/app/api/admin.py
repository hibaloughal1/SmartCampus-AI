from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.session import get_db
from app.auth.dependencies import require_admin
from app.models.user import User, UserRole
from app.models.department import Department, Subject
from app.schemas.user import UserOut, UserUpdate

router = APIRouter(prefix="/api/admin", tags=["Administration"])


class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None


class DepartmentOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class SubjectCreate(BaseModel):
    name: str
    department_id: Optional[str] = None


class SubjectOut(BaseModel):
    id: str
    name: str
    department_id: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(user_id: str, payload: UserUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: str, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    db.delete(user)
    db.commit()
    return None


@router.post("/departments", response_model=DepartmentOut, status_code=201)
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    dept = Department(name=payload.name, description=payload.description)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.get("/departments", response_model=List[DepartmentOut])
def list_departments(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(Department).all()


@router.delete("/departments/{dept_id}", status_code=204)
def delete_department(dept_id: str, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Département introuvable")
    db.delete(dept)
    db.commit()
    return None


@router.post("/subjects", response_model=SubjectOut, status_code=201)
def create_subject(payload: SubjectCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    subject = Subject(name=payload.name, department_id=payload.department_id)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


@router.get("/subjects", response_model=List[SubjectOut])
def list_subjects(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(Subject).all()


@router.delete("/subjects/{subject_id}", status_code=204)
def delete_subject(subject_id: str, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matière introuvable")
    db.delete(subject)
    db.commit()
    return None


@router.post("/rebuild-index", status_code=200)
def rebuild_index(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    from app.services.document_service import rebuild_bm25_index
    rebuild_bm25_index(db)
    return {"detail": "Index BM25 reconstruit avec succès."}
