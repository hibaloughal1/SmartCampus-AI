"""
In-memory BM25 lexical index, rebuilt from the `chunks` table. Kept simple
(rank_bm25) and complements FAISS semantic search for the hybrid retrieval
strategy described in the cahier des charges (section 5.9).
"""
import threading
from typing import List, Tuple

from rank_bm25 import BM25Okapi

_lock = threading.Lock()
_bm25: BM25Okapi = None
_corpus_ids: List[str] = []  # chunk_id per corpus entry, aligned with _bm25 tokenized corpus


def _tokenize(text: str) -> List[str]:
    return text.lower().split()


def build_index(chunk_rows: List[Tuple[str, str]]):
    """chunk_rows: list of (chunk_id, content)"""
    global _bm25, _corpus_ids
    with _lock:
        if not chunk_rows:
            _bm25 = None
            _corpus_ids = []
            return
        tokenized = [_tokenize(content) for _, content in chunk_rows]
        _bm25 = BM25Okapi(tokenized)
        _corpus_ids = [chunk_id for chunk_id, _ in chunk_rows]


def search(query: str, top_k: int = 5) -> List[Tuple[str, float]]:
    """Returns list of (chunk_id, bm25_score)."""
    with _lock:
        if _bm25 is None or not _corpus_ids:
            return []
        scores = _bm25.get_scores(_tokenize(query))
        ranked = sorted(zip(_corpus_ids, scores), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]


def is_built() -> bool:
    return _bm25 is not None
