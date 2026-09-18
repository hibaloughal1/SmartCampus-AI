"""
Hybrid retrieval: fuses FAISS (semantic / vector) results with BM25
(lexical) results via weighted score fusion, as specified in section 5.9
of the cahier des charges. Falls back gracefully to whichever index has
data if the other is empty.
"""
from typing import List, Dict

from sqlalchemy.orm import Session

from app.config import settings
from app.rag import bm25_index
from app.rag.embeddings import embed_query
from app.rag.vector_store import get_vector_store
from app.models.chunk import Chunk
from app.models.document import Document

VECTOR_WEIGHT = 0.6
BM25_WEIGHT = 0.4


def _normalize(scores: Dict[str, float]) -> Dict[str, float]:
    if not scores:
        return {}
    values = list(scores.values())
    lo, hi = min(values), max(values)
    if hi - lo < 1e-9:
        return {k: 1.0 for k in scores}
    return {k: (v - lo) / (hi - lo) for k, v in scores.items()}


def hybrid_search(db: Session, query: str, top_k: int = None) -> List[dict]:
    """Returns a ranked list of {chunk, document, score} dicts, fused from
    vector search and BM25, filtered by the anti-hallucination similarity
    threshold."""
    top_k = top_k or settings.TOP_K_RESULTS
    candidate_pool = max(top_k * 3, 10)

    # 1. Vector (semantic) search
    query_vec = embed_query(query)
    vector_hits = get_vector_store().search(query_vec, top_k=candidate_pool)
    vector_scores: Dict[str, float] = {}
    for meta, score in vector_hits:
        vector_scores[meta["chunk_id"]] = score

    # 2. Lexical (BM25) search
    bm25_scores: Dict[str, float] = {}
    if bm25_index.is_built():
        for chunk_id, score in bm25_index.search(query, top_k=candidate_pool):
            bm25_scores[chunk_id] = score

    # 3. Weighted fusion of normalized scores
    norm_vector = _normalize(vector_scores)
    norm_bm25 = _normalize(bm25_scores)
    all_chunk_ids = set(norm_vector) | set(norm_bm25)

    fused_scores = {}
    for cid in all_chunk_ids:
        fused_scores[cid] = (
            VECTOR_WEIGHT * norm_vector.get(cid, 0.0)
            + BM25_WEIGHT * norm_bm25.get(cid, 0.0)
        )

    ranked_ids = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    if not ranked_ids:
        return []

    # 4. Hydrate with DB content, apply anti-hallucination threshold using the
    #    raw vector similarity (best available "confidence" signal per chunk)
    chunk_ids = [cid for cid, _ in ranked_ids]
    chunks = db.query(Chunk).filter(Chunk.id.in_(chunk_ids)).all()
    chunks_by_id = {c.id: c for c in chunks}

    results = []
    for cid, fused_score in ranked_ids:
        chunk = chunks_by_id.get(cid)
        if not chunk:
            continue
        raw_vector_score = vector_scores.get(cid, fused_score)
        if raw_vector_score < settings.SIMILARITY_THRESHOLD and cid not in bm25_scores:
            continue  # neither semantically nor lexically relevant enough
        document = db.query(Document).filter(Document.id == chunk.document_id).first()
        results.append({
            "chunk": chunk,
            "document": document,
            "score": fused_score,
        })

    return results
