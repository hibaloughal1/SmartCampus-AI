"""
Basic functional tests: app import, chunking fallback, password hashing.
Run with: pytest
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_app_imports():
    from app.main import app
    assert app is not None


def test_password_hash_roundtrip():
    from app.auth.security import hash_password, verify_password
    hashed = hash_password("MonMotDePasse123")
    assert verify_password("MonMotDePasse123", hashed)
    assert not verify_password("mauvais_mdp", hashed)


def test_jwt_roundtrip():
    from app.auth.security import create_access_token, decode_access_token
    token = create_access_token({"sub": "user-123"})
    payload = decode_access_token(token)
    assert payload["sub"] == "user-123"


def test_pure_python_chunking_fallback():
    from app.rag.chunking import _chunk_pure_python
    text = " ".join([f"mot{i}" for i in range(300)])
    chunks = _chunk_pure_python(text, chunk_size=500, chunk_overlap=100)
    assert len(chunks) > 0
    assert all(isinstance(c, str) and c.strip() for c in chunks)


def test_role_enforcement_dependency_exists():
    from app.auth.dependencies import require_admin, get_current_user
    assert callable(require_admin)
    assert callable(get_current_user)
