"""
SmartCampus AI - FastAPI application entry point.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.session import init_db, SessionLocal
from app.services.document_service import rebuild_bm25_index
from app.api import (
    auth_router, documents_router, chat_router, quiz_router,
    dashboard_router, admin_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables if missing, and warm up the BM25 lexical index
    # from whatever chunks already exist in MySQL.
    init_db()
    db = SessionLocal()
    try:
        rebuild_bm25_index(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Assistant universitaire intelligent basé sur le Retrieval-Augmented Generation (RAG)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(documents_router.router)
app.include_router(chat_router.router)
app.include_router(quiz_router.router)
app.include_router(dashboard_router.router)
app.include_router(admin_router.router)


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "status": "running"}


@app.get("/api/health")
async def health_check():
    from app.rag.llm_client import get_llm_client
    ollama_ok = await get_llm_client().health_check()
    return {"status": "ok", "database": "mysql", "ollama_reachable": ollama_ok}
