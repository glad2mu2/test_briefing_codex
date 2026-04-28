"""Tests for article summarization post-processing."""

from __future__ import annotations

from typing import Any

import pytest

from src.agents.article_summarizer import summarize_article
from src.config import SUMMARY_MAX_CHARS, load_settings
from src.llm.client import LLMClient
from src.schemas import Article


class FakeResponses:
    async def create(self, **_: Any) -> dict[str, str]:
        return {"output_text": "{\"summary\": \"" + ("가" * 250) + "\"}"}


class FakeOpenAIClient:
    responses = FakeResponses()


@pytest.mark.asyncio
async def test_summarizer_enforces_summary_length() -> None:
    settings = load_settings({"USE_OPENAI_AGENTS_SDK": "false"})
    client = LLMClient(settings, client=FakeOpenAIClient())
    article = Article(
        article_id="a1",
        issue_id="i1",
        title="건설 경기 기사",
        source="대한경제",
        url="https://example.com/article",
        body="본문",
    )

    summary = await summarize_article(article, client, settings)

    assert len(summary.summary) == SUMMARY_MAX_CHARS
    assert summary.source == "대한경제"
    assert summary.url == "https://example.com/article"
