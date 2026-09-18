"""
Builds the final prompt sent to the LLM: system instructions + conversation
memory (last N messages) + retrieved documents + the user's question, per
section 5.11 of the cahier des charges.
"""
from typing import List

SYSTEM_PROMPT = (
    "Tu es SmartCampus AI, un assistant universitaire intelligent. "
    "Réponds UNIQUEMENT à partir des documents fournis dans le contexte ci-dessous. "
    "Si la réponse ne se trouve pas dans les documents fournis, indique clairement "
    "que l'information est indisponible dans la base documentaire, sans inventer de réponse. "
    "Cite les documents que tu utilises. Réponds de manière claire, concise et structurée."
)


def build_prompt(question: str, retrieved_chunks: List[dict], conversation_history: List[dict]) -> str:
    parts = []

    if conversation_history:
        parts.append("### Historique de la conversation :")
        for msg in conversation_history:
            role = "Étudiant" if msg["role"] == "user" else "Assistant"
            parts.append(f"{role}: {msg['content']}")
        parts.append("")

    if retrieved_chunks:
        parts.append("### Documents pertinents :")
        for i, item in enumerate(retrieved_chunks, start=1):
            doc_title = item["document"].title if item["document"] else "Document inconnu"
            parts.append(f"[Source {i} - {doc_title}]\n{item['chunk'].content}")
        parts.append("")
    else:
        parts.append("### Aucun document pertinent n'a été trouvé dans la base documentaire.")
        parts.append("")

    parts.append(f"### Question de l'étudiant :\n{question}")

    return "\n".join(parts)


def has_sufficient_context(retrieved_chunks: List[dict]) -> bool:
    return len(retrieved_chunks) > 0
