from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.user import UserOut, UserUpdate
from app.auth.dependencies import require_admin
from app.models.user import User
from app.models.department import Department, Subject
from pydantic import BaseModel

router = APIRouter(prefix="/api/admin", tags=["Administration"])


@router.get("/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: str, payload: UserUpdate, db: Session = Depends(get_db),
                 current_user: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    db.delete(user)
    db.commit()


class DepartmentIn(BaseModel):
    name: str
    description: str | None = None


class SubjectIn(BaseModel):
    name: str
    department_id: str | None = None


@router.get("/departments")
def list_departments(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return db.query(Department).all()


@router.post("/departments", status_code=201)
def create_department(payload: DepartmentIn, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    dept = Department(name=payload.name, description=payload.description)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.get("/subjects")
def list_subjects(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return db.query(Subject).all()


@router.post("/subjects", status_code=201)
def create_subject(payload: SubjectIn, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    subject = Subject(name=payload.name, department_id=payload.department_id)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject
