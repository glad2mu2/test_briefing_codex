"""Tests for LLM privacy gates."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.config import load_settings
from src.llm.client import (
    DataTransferNotAllowedError,
    LLMClient,
    TextTransferRequest,
)


def test_text_transfer_disabled_by_default() -> None:
    client = LLMClient(load_settings({}))
    request = TextTransferRequest(
        purpose="pdf_issue_extraction",
        source_path=Path("sample.pdf"),
        page_numbers=(1,),
        text="건설 경기 전망",
    )

    with pytest.raises(DataTransferNotAllowedError):
        client.require_text_transfer_allowed(request)


def test_text_transfer_allowed_when_env_enabled() -> None:
    client = LLMClient(load_settings({"ALLOW_OPENAI_TEXT_UPLOAD": "true"}))
    request = TextTransferRequest(
        purpose="pdf_issue_extraction",
        source_path=Path("sample.pdf"),
        page_numbers=(1,),
        text="건설 경기 전망",
    )

    transfer = client.require_text_transfer_allowed(request)

    assert transfer.provider == "openai"
    assert transfer.char_count == len("건설 경기 전망")
    assert transfer.page_numbers == (1,)
