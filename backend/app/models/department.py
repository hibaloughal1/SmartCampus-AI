import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR

from app.database.session import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Department(Base):
    __tablename__ = "departments"

    id = Column(CHAR(36), primary_key=True, default=gen_uuid)
    name = Column(String(150), unique=True, nullable=False)
    description = Column(String(500), nullable=True)

    users = relationship("User", back_populates="department")
    subjects = relationship("Subject", back_populates="department", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(CHAR(36), primary_key=True, default=gen_uuid)
    name = Column(String(150), nullable=False)
    department_id = Column(CHAR(36), ForeignKey("departments.id"), nullable=True)

    department = relationship("Department", back_populates="subjects")
    documents = relationship("Document", back_populates="subject")
