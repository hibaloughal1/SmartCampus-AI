"""
Main RAG orchestrator: ties together retrieval, prompt construction,
the LLM client, and hallucination safeguards into a single entry point
used by the chat service.
"""
import json
import time
from typing import List, Optional

from sqlalchemy.orm import Session

from app.rag.retrieval import hybrid_search
from app.rag.prompt_builder import build_prompt, has_sufficient_context, SYSTEM_PROMPT
from app.rag.memory import get_recent_history
from app.rag.llm_client import get_llm_client, OllamaUnavailableError

NO_CONTEXT_ANSWER = (
    "Je n'ai trouvé aucune information pertinente dans les documents disponibles "
    "pour répondre à cette question. Merci de reformuler ou de consulter un enseignant."
)


class RAGResponse:
    def __init__(self, answer: str, sources: list, response_time_ms: float):
        self.answer = answer
        self.sources = sources
        self.response_time_ms = response_time_ms


async def answer_question(db: Session, question: str, conversation_id: Optional[str] = None) -> RAGResponse:
    start = time.perf_counter()

    retrieved = hybrid_search(db, question)
    history = get_recent_history(db, conversation_id) if conversation_id else []

    if not has_sufficient_context(retrieved):
        elapsed_ms = (time.perf_counter() - start) * 1000
        return RAGResponse(answer=NO_CONTEXT_ANSWER, sources=[], response_time_ms=elapsed_ms)

    prompt = build_prompt(question, retrieved, history)

    try:
        llm = get_llm_client()
        answer = await llm.generate(prompt=prompt, system=SYSTEM_PROMPT)
    except OllamaUnavailableError as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return RAGResponse(
            answer=f"Le modèle de langage local (Ollama) est actuellement injoignable : {e}",
            sources=[],
            response_time_ms=elapsed_ms,
        )

    sources = [
        {
            "document_id": item["document"].id if item["document"] else "",
            "document_title": item["document"].title if item["document"] else "Inconnu",
            "chunk_content": item["chunk"].content[:300],
            "score": round(item["score"], 4),
        }
        for item in retrieved
    ]

    elapsed_ms = (time.perf_counter() - start) * 1000
    return RAGResponse(answer=answer, sources=sources, response_time_ms=elapsed_ms)


async def generate_summary(context_text: str) -> str:
    llm = get_llm_client()
    prompt = (
        "Résume le texte suivant de façon claire et structurée, en conservant les "
        "points clés, sans ajouter d'informations qui n'y figurent pas :\n\n" + context_text
    )
    return await llm.generate(prompt=prompt, system=SYSTEM_PROMPT)


async def generate_quiz_json(context_text: str, num_questions: int = 5) -> list:
    """Asks the LLM to produce a strict JSON array of MCQ questions, then
    parses it defensively (LLMs sometimes wrap JSON in prose or code fences)."""
    llm = get_llm_client()
    prompt = (
        f"À partir du texte ci-dessous, génère exactement {num_questions} questions à choix "
        "multiples (QCM) au format JSON STRICT, sans aucun texte avant ou après, sous la forme "
        "d'une liste d'objets avec les clés : question, option_a, option_b, option_c, option_d, "
        "correct_option (une lettre parmi A, B, C, D), explanation.\n\n"
        f"Texte :\n{context_text}"
    )
    raw = await llm.generate(prompt=prompt, system="Tu réponds uniquement en JSON valide.", temperature=0.4)
    return _safe_parse_json_list(raw)


async def generate_flashcards_json(context_text: str, num_cards: int = 10) -> list:
    llm = get_llm_client()
    prompt = (
        f"À partir du texte ci-dessous, génère exactement {num_cards} fiches de révision (flashcards) "
        "au format JSON STRICT, sans aucun texte avant ou après, sous la forme d'une liste d'objets "
        "avec les clés : front (question ou terme) et back (réponse ou définition).\n\n"
        f"Texte :\n{context_text}"
    )
    raw = await llm.generate(prompt=prompt, system="Tu réponds uniquement en JSON valide.", temperature=0.4)
    return _safe_parse_json_list(raw)


def _safe_parse_json_list(raw: str) -> list:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()
    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
        return []
    except json.JSONDecodeError:
        start = cleaned.find("[")
        end = cleaned.rfind("]")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(cleaned[start:end + 1])
            except json.JSONDecodeError:
                return []
        return []
