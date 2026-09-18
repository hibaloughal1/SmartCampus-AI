"""
Extracts raw text from uploaded documents (PDF, DOCX, PPTX, TXT).
"""
from pathlib import Path

from pypdf import PdfReader
from docx import Document as DocxDocument
from pptx import Presentation


class DocumentProcessor:
    """Extracts and lightly normalizes text from supported file types."""

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".txt"}

    @classmethod
    def is_supported(cls, filename: str) -> bool:
        return Path(filename).suffix.lower() in cls.SUPPORTED_EXTENSIONS

    @classmethod
    def extract_text(cls, file_path: str) -> str:
        suffix = Path(file_path).suffix.lower()
        if suffix == ".pdf":
            return cls._extract_pdf(file_path)
        if suffix == ".docx":
            return cls._extract_docx(file_path)
        if suffix == ".pptx":
            return cls._extract_pptx(file_path)
        if suffix == ".txt":
            return cls._extract_txt(file_path)
        raise ValueError(f"Format de fichier non supporté : {suffix}")

    @staticmethod
    def _extract_pdf(file_path: str) -> str:
        reader = PdfReader(file_path)
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)
        return "\n".join(pages)

    @staticmethod
    def _extract_docx(file_path: str) -> str:
        doc = DocxDocument(file_path)
        parts = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                parts.append(" | ".join(cell.text for cell in row.cells))
        return "\n".join(parts)

    @staticmethod
    def _extract_pptx(file_path: str) -> str:
        prs = Presentation(file_path)
        parts = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for para in shape.text_frame.paragraphs:
                        text = "".join(run.text for run in para.runs)
                        if text.strip():
                            parts.append(text)
        return "\n".join(parts)

    @staticmethod
    def _extract_txt(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    @staticmethod
    def clean_text(text: str) -> str:
        """Basic cleaning: collapse whitespace, strip control chars."""
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]
        return "\n".join(lines)
