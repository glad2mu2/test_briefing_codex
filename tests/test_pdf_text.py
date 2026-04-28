"""Tests for src.extractors.pdf_text."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.extractors.pdf_text import looks_garbled


def test_looks_garbled_empty_string_returns_false() -> None:
    assert looks_garbled("") is False


def test_looks_garbled_clean_korean_text() -> None:
    assert looks_garbled("건설업 주간 브리핑입니다") is False


def test_looks_garbled_mostly_replacement_chars() -> None:
    assert looks_garbled("����ok") is True


def test_looks_garbled_low_replacement_ratio() -> None:
    assert looks_garbled("a long clean english string with one �") is False


def test_looks_garbled_threshold_override() -> None:
    text = "ab�"  # ratio = 1/3 ≈ 0.333
    assert looks_garbled(text, threshold=0.5) is False
    assert looks_garbled(text, threshold=0.3) is True


def test_extract_raises_on_missing_file(tmp_path: Path) -> None:
    from src.extractors.pdf_text import extract_text_from_pdf

    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf(tmp_path / "nope.pdf")


def test_extract_raises_on_invalid_pdf(tmp_path: Path) -> None:
    from src.extractors.pdf_text import (
        PDFExtractionError,
        extract_text_from_pdf,
    )

    bogus = tmp_path / "bogus.pdf"
    bogus.write_bytes(b"this is not a valid PDF")
    with pytest.raises(PDFExtractionError, match="failed to extract"):
        extract_text_from_pdf(bogus)
