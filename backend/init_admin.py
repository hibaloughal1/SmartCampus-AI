"""
One-off script: creates a default admin account if none exists yet.
Run with: python init_admin.py
"""
from app.database.session import SessionLocal, init_db
from app.models.user import User, UserRole
from app.auth.security import hash_password

DEFAULT_ADMIN_EMAIL = "admin@smartcampus.ai"
DEFAULT_ADMIN_PASSWORD = "Admin@12345"


def main():
    init_db()
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing:
            print(f"Un administrateur existe déjà : {existing.email}")
            return
        admin = User(
            full_name="Administrateur SmartCampus",
            email=DEFAULT_ADMIN_EMAIL,
            hashed_password=hash_password(DEFAULT_ADMIN_PASSWORD),
            role=UserRole.ADMIN,
        )
        db.add(admin)
        db.commit()
        print(f"Compte administrateur créé : {DEFAULT_ADMIN_EMAIL} / {DEFAULT_ADMIN_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
