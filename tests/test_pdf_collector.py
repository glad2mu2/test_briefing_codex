"""Tests for src.collectors.pdf_collector."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import pytest

from src.collectors.pdf_collector import (
    PDFValidationError,
    validate_uploaded_pdf,
)
from src.config import MAX_UPLOAD_PDF_SIZE_MB

_VALID_PDF_BYTES = b"%PDF-1.4\n%minimal\n"


@pytest.fixture
def valid_pdf(tmp_path: Path) -> Path:
    p = tmp_path / "sample.pdf"
    p.write_bytes(_VALID_PDF_BYTES)
    return p


def test_validate_returns_metadata(valid_pdf: Path) -> None:
    result = validate_uploaded_pdf(valid_pdf)
    assert result.source == "upload"
    assert result.local_path == valid_pdf
    assert result.original_filename == "sample.pdf"
    assert result.size_bytes == len(_VALID_PDF_BYTES)
    assert result.url is None
    assert isinstance(result.collected_at, datetime)


def test_validate_missing_file(tmp_path: Path) -> None:
    with pytest.raises(PDFValidationError, match="file not found"):
        validate_uploaded_pdf(tmp_path / "missing.pdf")


def test_validate_directory_path(tmp_path: Path) -> None:
    with pytest.raises(PDFValidationError, match="not a regular file"):
        validate_uploaded_pdf(tmp_path)


def test_validate_empty_file(tmp_path: Path) -> None:
    p = tmp_path / "empty.pdf"
    p.write_bytes(b"")
    with pytest.raises(PDFValidationError, match="empty file"):
        validate_uploaded_pdf(p)


def test_validate_too_large(tmp_path: Path) -> None:
    p = tmp_path / "huge.pdf"
    p.touch()
    os.truncate(p, MAX_UPLOAD_PDF_SIZE_MB * 1024 * 1024 + 1)
    with pytest.raises(PDFValidationError, match="too large"):
        validate_uploaded_pdf(p)


def test_validate_wrong_magic_bytes(tmp_path: Path) -> None:
    # File has .pdf extension (MIME would say PDF) but magic bytes are not.
    p = tmp_path / "fake.pdf"
    p.write_bytes(b"NOPE!\n")
    with pytest.raises(PDFValidationError, match="not a PDF"):
        validate_uploaded_pdf(p)


def test_validate_wrong_extension_but_valid_magic(tmp_path: Path) -> None:
    # Magic bytes are authoritative; extension is not.
    p = tmp_path / "weirdname.bin"
    p.write_bytes(_VALID_PDF_BYTES)
    result = validate_uploaded_pdf(p)
    assert result.original_filename == "weirdname.bin"
