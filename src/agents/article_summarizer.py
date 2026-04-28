"""Article summarization specialist."""

from __future__ import annotations

from src.agents.openai_agent_runner import run_specialist_json
from src.config import SUMMARY_MAX_BYTES, SUMMARY_MIN_BYTES, AppSettings
from src.llm.client import LLMClient
from src.schemas import Article, ArticleSummary


async def summarize_article(
    article: Article,
    client: LLMClient,
    settings: AppSettings,
) -> ArticleSummary:
    """Summarize one article and enforce the configured Korean-character limit."""
    instructions = (
        "You summarize Korean construction news for executive PPT slides that "
        "management will read after the meeting. Return only JSON: "
        "{\"summary\": string}. The summary must be detailed enough to "
        "understand the article's main facts, causes, figures, stakeholders, "
        f"and implications. Use {SUMMARY_MIN_BYTES}-{SUMMARY_MAX_BYTES} UTF-8 bytes "
        "including spaces. "
        "Do not copy the article body verbatim."
    )
    payload = await run_specialist_json(
        name="article-summarizer",
        model=settings.models.summarization,
        instructions=instructions,
        user_input=(
            f"Title: {article.title}\n"
            f"Source: {article.source}\n"
            f"URL: {article.url}\n"
            f"Body:\n{article.body}"
        ),
        schema_name="article summary",
        settings=settings,
        fallback_client=client,
    )
    summary = payload.get("summary")
    summary_text = summary if isinstance(summary, str) else ""
    return ArticleSummary(
        article_id=article.article_id,
        issue_id=article.issue_id,
        title=article.title,
        source=article.source,
        url=article.url,
        summary=_truncate_utf8(summary_text, SUMMARY_MAX_BYTES),
        image_url=article.image_url,
    )


def _truncate_utf8(text: str, max_bytes: int) -> str:
    """Trim text to a UTF-8 byte budget without splitting characters."""
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return text
    trimmed = encoded[:max_bytes]
    while trimmed:
        try:
            return trimmed.decode("utf-8")
        except UnicodeDecodeError:
            trimmed = trimmed[:-1]
    return ""
