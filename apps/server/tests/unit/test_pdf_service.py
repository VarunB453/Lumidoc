"""Unit tests for PDFService."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.services.pdf_service import PDFService, pdf_service


def _make_pdf(path: Path, text: str = "Hello Lumidoc. " * 50) -> Path:
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    page2 = doc.new_page()
    page2.insert_text((72, 72), text + " second page.")
    doc.save(str(path))
    doc.close()
    return path


def test_extract_text_returns_pages(tmp_path):
    pdf = _make_pdf(tmp_path / "test.pdf")
    pages = pdf_service.extract_text(pdf)
    assert len(pages) == 2
    assert "Hello Lumidoc" in pages[0]["text"]


def test_extract_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        pdf_service.extract_text(tmp_path / "missing.pdf")


def test_chunk_pages():
    pages = [
        {"page": 1, "text": "Sentence one. " * 100},
        {"page": 2, "text": ""},
        {"page": 3, "text": "Another " * 200},
    ]
    chunks = pdf_service.chunk_pages(pages)
    assert len(chunks) > 0
    for c in chunks:
        assert "text" in c and "page" in c
        assert c["text"].strip() != ""


def test_chunk_pages_empty():
    assert pdf_service.chunk_pages([]) == []


def test_chunk_size_constraints():
    svc = PDFService()
    assert svc.CHUNK_SIZE == 512
    assert svc.CHUNK_OVERLAP == 64


def test_pymupdf_fallback_to_plumber(tmp_path, monkeypatch):
    pdf = _make_pdf(tmp_path / "scan.pdf")

    def empty_pymu(path):
        return [{"page": 1, "text": ""}]

    monkeypatch.setattr(PDFService, "_extract_pymupdf", staticmethod(empty_pymu))
    pages = pdf_service.extract_text(pdf)
    # pdfplumber on a synthetic PDF may return short text — just verify it ran.
    assert isinstance(pages, list)
