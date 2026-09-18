"""
Embedding generation using SentenceTransformers (all-MiniLM-L6-v2).
Model is loaded lazily (singleton) to avoid the cost at import time /
in environments where the model has not been downloaded yet.
"""
from typing import List
import numpy as np

from app.config import settings

_model = None


def get_embedding_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


def embed_texts(texts: List[str]) -> np.ndarray:
    """Returns an (n_texts, dim) float32 numpy array of normalized embeddings."""
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False, normalize_embeddings=True)
    return embeddings.astype("float32")


def embed_query(query: str) -> np.ndarray:
    return embed_texts([query])[0]
