"""
Chunking strategies for splitting document text into overlapping segments.

Primary path: LangChain's RecursiveCharacterTextSplitter.
Fallback path: pure-Python splitter (used automatically if LangChain is
unavailable or raises an error), so document processing never hard-fails
on this step.
"""
from typing import List

from app.config import settings


def chunk_text(text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[str]:
    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    try:
        return _chunk_with_langchain(text, chunk_size, chunk_overlap)
    except Exception:
        return _chunk_pure_python(text, chunk_size, chunk_overlap)


def _chunk_with_langchain(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(text)
    return [c.strip() for c in chunks if c.strip()]


def _chunk_pure_python(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """Simple sliding-window chunker with overlap, splitting on paragraph/word
    boundaries where possible. Used as a dependency-free fallback."""
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    # approximate characters-per-word to translate char chunk_size to word count
    avg_word_len = max(1, sum(len(w) for w in words) // len(words))
    words_per_chunk = max(1, chunk_size // (avg_word_len + 1))
    overlap_words = max(0, chunk_overlap // (avg_word_len + 1))

    while start < len(words):
        end = min(start + words_per_chunk, len(words))
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk.strip())
        if end == len(words):
            break
        start = end - overlap_words if (end - overlap_words) > start else end

    return chunks
