"""PDF collectors. Layer 1 (deterministic Python) per DESIGN.md §5.1."""

from src.collectors.pdf_collector import (
    CollectedPDF,
    PDFValidationError,
    validate_uploaded_pdf,
)

__all__ = [
    "CollectedPDF",
    "PDFValidationError",
    "validate_uploaded_pdf",
]
