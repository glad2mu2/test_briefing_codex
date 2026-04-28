"""Text and media extraction. Layer 1 (deterministic) per DESIGN.md §5.1."""

from src.extractors.pdf_text import (
    ExtractedPage,
    ExtractedPDF,
    PDFExtractionError,
    extract_text_from_pdf,
    looks_garbled,
)

__all__ = [
    "ExtractedPDF",
    "ExtractedPage",
    "PDFExtractionError",
    "extract_text_from_pdf",
    "looks_garbled",
]
