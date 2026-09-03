"""PDF validation and page-by-page text extraction using PyMuPDF."""

import logging

import pymupdf as fitz

from app.core.exceptions import InvalidPdfError
from app.rag.chunker import PageText
from app.utils.text_utils import clean_text

logger = logging.getLogger("evidencerag")


def extract_pages(file_bytes: bytes) -> list[PageText]:
    """Extract cleaned text for every page of a PDF.

    Raises InvalidPdfError if the file cannot be opened/parsed as a PDF.
    """
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
            pages: list[PageText] = []
            for index in range(pdf.page_count):
                raw_text = pdf.load_page(index).get_text()
                pages.append(PageText(page=index + 1, text=clean_text(raw_text)))
            return pages
    except InvalidPdfError:
        raise
    except Exception as exc:  # PyMuPDF raises varied exception types for bad files
        logger.warning("pdf_open_failed", extra={"error": str(exc)})
        raise InvalidPdfError("Unable to process this PDF.") from exc


def is_readable_pdf(file_bytes: bytes) -> bool:
    """Best-effort check that a file is a genuinely readable PDF, not just named .pdf."""
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
            return pdf.page_count > 0
    except Exception:
        return False
