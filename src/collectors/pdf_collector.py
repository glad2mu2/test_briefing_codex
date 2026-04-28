"""PDF collection from uploads and trusted sources (KFCC/CERIK).

Layer 1 — deterministic, no AI. See DESIGN.md §5.1.
"""

from __future__ import annotations

import logging
import mimetypes
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.config import MAX_UPLOAD_PDF_SIZE_MB

logger = logging.getLogger(__name__)

_PDF_MAGIC = b"%PDF-"


@dataclass(frozen=True)
class CollectedPDF:
    """Metadata for a single collected PDF, used by downstream pipeline.

    Attributes:
        source: Origin label (e.g., "upload", "KFCC", "CERIK").
        local_path: Path to the PDF on local disk.
        collected_at: When the file was collected.
        original_filename: Original filename for display / traceability.
        size_bytes: File size in bytes.
        url: Source URL if remotely collected; None for uploads.
    """

    source: str
    local_path: Path
    collected_at: datetime
    original_filename: str
    size_bytes: int
    url: str | None = None


class PDFValidationError(ValueError):
    """Raised when a PDF fails validation (size, MIME, magic-bytes)."""


def validate_uploaded_pdf(path: Path) -> CollectedPDF:
    """Validate a user-uploaded PDF and wrap as CollectedPDF.

    Validates:
        - File exists and is a regular file
        - Size > 0 and <= MAX_UPLOAD_PDF_SIZE_MB
        - Magic bytes start with ``%PDF-`` (authoritative; MIME used only
          for diagnostics)

    Args:
        path: Local path to the uploaded file.

    Returns:
        CollectedPDF metadata for the validated file.

    Raises:
        PDFValidationError: If any validation check fails.
    """
    if not path.exists():
        raise PDFValidationError(f"file not found: {path}")
    if not path.is_file():
        raise PDFValidationError(f"not a regular file: {path}")

    size_bytes = path.stat().st_size
    if size_bytes == 0:
        raise PDFValidationError(f"empty file: {path}")
    max_bytes = MAX_UPLOAD_PDF_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        raise PDFValidationError(
            f"file too large: {size_bytes} bytes "
            f"(max {MAX_UPLOAD_PDF_SIZE_MB} MB = {max_bytes} bytes)"
        )

    with path.open("rb") as f:
        magic = f.read(len(_PDF_MAGIC))
    if magic != _PDF_MAGIC:
        mime, _ = mimetypes.guess_type(path)
        raise PDFValidationError(
            f"not a PDF: mime={mime!r}, magic={magic!r}"
        )

    pdf = CollectedPDF(
        source="upload",
        local_path=path,
        collected_at=datetime.now(),
        original_filename=path.name,
        size_bytes=size_bytes,
    )
    logger.info("validated upload: %s (%d bytes)", path.name, size_bytes)
    return pdf


# TODO: KFCCCollector — fetch list, filter last 7 days, download via httpx
# TODO: CERIKCollector — requires playwright (React-based dynamic page)
