"""PDF text extraction.

Layer 1 — deterministic. See DESIGN.md and AGENTS.md.

Encoding gotcha: KFCC PDFs sometimes embed EUC-KR text. Default pdfplumber
output may look garbled. Strategy: try pdfplumber → fall back to pypdf if
text looks garbled → defer OCR to caller (heavy dependency).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pdfplumber

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExtractedPage:
    """Single page of extracted text + provenance for fallback debugging."""

    page_number: int
    text: str
    extractor_used: str  # "pdfplumber" | "pypdf" | "ocr"


@dataclass(frozen=True)
class ExtractedPDF:
    """All pages from one PDF + summary."""

    source_path: Path
    pages: tuple[ExtractedPage, ...]
    total_chars: int


class PDFExtractionError(RuntimeError):
    """Raised when PDF cannot be opened or all extractors fail."""


def extract_text_from_pdf(path: Path) -> ExtractedPDF:
    """Extract text from all pages of a PDF using pdfplumber.

    Args:
        path: Path to the PDF file.

    Returns:
        ExtractedPDF with per-page results and total character count.

    Raises:
        FileNotFoundError: If path does not exist.
        PDFExtractionError: If the PDF cannot be opened or parsed.
    """
    if not path.exists():
        raise FileNotFoundError(path)

    pages: list[ExtractedPage] = []
    try:
        with pdfplumber.open(path) as pdf:
            for idx, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                pages.append(
                    ExtractedPage(
                        page_number=idx,
                        text=text,
                        extractor_used="pdfplumber",
                    )
                )
    except Exception as exc:
        raise PDFExtractionError(f"failed to extract {path}: {exc}") from exc

    total = sum(len(p.text) for p in pages)
    logger.info(
        "extracted %s: %d pages, %d chars", path.name, len(pages), total
    )
    return ExtractedPDF(source_path=path, pages=tuple(pages), total_chars=total)


def looks_garbled(text: str, threshold: float = 0.3) -> bool:
    """Heuristic: high ratio of replacement chars suggests encoding issue.

    Used by orchestrator to decide whether to retry with pypdf or OCR.

    Args:
        text: Extracted text to inspect.
        threshold: Ratio of replacement chars above which text is flagged.

    Returns:
        True if more than ``threshold`` of chars are U+FFFD; False otherwise.
        Empty input returns False (nothing to judge).
    """
    if not text:
        return False
    bad = text.count("�")
    return bad / len(text) > threshold


# TODO: extract_with_pypdf — fallback when pdfplumber output looks garbled
# TODO: extract_with_ocr — final fallback (pdf2image + pytesseract)
