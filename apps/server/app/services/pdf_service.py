"""PDF text extraction + chunking service."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.logging import get_logger

logger = get_logger("pdf")


class PDFService:
    """Extract text from PDFs (PyMuPDF primary, pdfplumber fallback) + chunk."""

    CHUNK_SIZE = 512
    CHUNK_OVERLAP = 64

    def __init__(self) -> None:
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.CHUNK_SIZE,
            chunk_overlap=self.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )

    def extract_text(self, pdf_path: str | Path) -> list[dict[str, Any]]:
        """Extract per-page text. Returns [{page, text}, ...]."""
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")

        pages = self._extract_pymupdf(path)
        # If PyMuPDF returned no text (likely scanned PDF) fallback to pdfplumber.
        non_empty = [p for p in pages if p["text"].strip()]
        if not non_empty:
            logger.info("pymupdf_empty_falling_back_to_pdfplumber", path=str(path))
            pages = self._extract_pdfplumber(path)
        return pages

    @staticmethod
    def _extract_pymupdf(path: Path) -> list[dict[str, Any]]:
        try:
            import fitz  # PyMuPDF
        except ImportError as e:  # pragma: no cover
            raise RuntimeError("PyMuPDF (fitz) is not installed.") from e

        out: list[dict[str, Any]] = []
        with fitz.open(str(path)) as doc:
            for idx, page in enumerate(doc, start=1):
                try:
                    text = page.get_text("text") or ""
                except Exception as e:
                    logger.warning("page_extract_failed", page=idx, error=str(e))
                    text = ""
                out.append({"page": idx, "text": text})
        return out

    @staticmethod
    def _extract_pdfplumber(path: Path) -> list[dict[str, Any]]:
        try:
            import pdfplumber
        except ImportError as e:  # pragma: no cover
            raise RuntimeError("pdfplumber is not installed.") from e

        out: list[dict[str, Any]] = []
        with pdfplumber.open(str(path)) as pdf:
            for idx, page in enumerate(pdf.pages, start=1):
                try:
                    text = page.extract_text() or ""
                except Exception as e:
                    logger.warning("plumber_page_failed", page=idx, error=str(e))
                    text = ""
                out.append({"page": idx, "text": text})
        return out

    def chunk_pages(self, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Split per-page text into overlapping chunks. Returns [{text, page}, ...]."""
        chunks: list[dict[str, Any]] = []
        for page in pages:
            text = page["text"].strip()
            if not text:
                continue
            for piece in self.splitter.split_text(text):
                if piece.strip():
                    chunks.append({"text": piece, "page": page["page"]})
        logger.info("pdf_chunked", chunks=len(chunks))
        return chunks


pdf_service = PDFService()
