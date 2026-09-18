"""
FAISS-backed vector store. Persists the index and an id-map (chunk metadata)
to disk under settings.VECTOR_STORE_PATH so it survives restarts.
"""
import json
import os
import threading
from typing import List, Tuple, Optional

import numpy as np

from app.config import settings

_lock = threading.Lock()


class VectorStore:
    def __init__(self, dim: int = 384):
        self.dim = dim
        self.index_path = os.path.join(settings.VECTOR_STORE_PATH, "faiss.index")
        self.meta_path = os.path.join(settings.VECTOR_STORE_PATH, "meta.json")
        os.makedirs(settings.VECTOR_STORE_PATH, exist_ok=True)
        self._index = None
        self._metadata: List[dict] = []  # position -> {chunk_id, document_id}
        self._load()

    def _get_faiss(self):
        import faiss
        return faiss

    def _load(self):
        faiss = self._get_faiss()
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self._index = faiss.read_index(self.index_path)
            with open(self.meta_path, "r") as f:
                self._metadata = json.load(f)
        else:
            self._index = faiss.IndexFlatIP(self.dim)  # cosine sim via inner product on normalized vecs
            self._metadata = []

    def _save(self):
        faiss = self._get_faiss()
        faiss.write_index(self._index, self.index_path)
        with open(self.meta_path, "w") as f:
            json.dump(self._metadata, f)

    def add(self, vectors: np.ndarray, metadata: List[dict]) -> List[int]:
        """Adds vectors + metadata, returns the assigned FAISS positions (indices)."""
        with _lock:
            start_pos = self._index.ntotal
            self._index.add(vectors)
            self._metadata.extend(metadata)
            self._save()
            return list(range(start_pos, start_pos + len(metadata)))

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[dict, float]]:
        with _lock:
            if self._index.ntotal == 0:
                return []
            query_vector = query_vector.reshape(1, -1)
            scores, indices = self._index.search(query_vector, min(top_k, self._index.ntotal))
            results = []
            for idx, score in zip(indices[0], scores[0]):
                if idx == -1:
                    continue
                results.append((self._metadata[idx], float(score)))
            return results

    def remove_document(self, document_id: str):
        """FAISS IndexFlatIP doesn't support deletion in place efficiently, so
        we rebuild the index excluding the given document's vectors. Suitable
        for a moderate-sized university document corpus."""
        with _lock:
            faiss = self._get_faiss()
            keep_positions = [i for i, m in enumerate(self._metadata) if m.get("document_id") != document_id]
            if len(keep_positions) == len(self._metadata):
                return  # nothing to remove
            if not keep_positions:
                self._index = faiss.IndexFlatIP(self.dim)
                self._metadata = []
            else:
                old_vectors = self._index.reconstruct_n(0, self._index.ntotal)
                new_vectors = old_vectors[keep_positions]
                new_metadata = [self._metadata[i] for i in keep_positions]
                new_index = faiss.IndexFlatIP(self.dim)
                new_index.add(new_vectors)
                self._index = new_index
                self._metadata = new_metadata
            self._save()


_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
