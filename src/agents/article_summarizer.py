"""Article summarization specialist."""

from __future__ import annotations

from src.agents.openai_agent_runner import run_specialist_json
from src.config import SUMMARY_MAX_CHARS, AppSettings
from src.llm.client import LLMClient
from src.schemas import Article, ArticleSummary


async def summarize_article(
    article: Article,
    client: LLMClient,
    settings: AppSettings,
) -> ArticleSummary:
    """Summarize one article and enforce the 200 Korean-character limit."""
    instructions = (
        "You summarize Korean construction news for executive PPT slides. "
        f"Return only JSON: {{\"summary\": string}}. The summary must be "
        f"{SUMMARY_MAX_CHARS} Korean characters or fewer. Do not copy the "
        "article body verbatim."
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
        summary=summary_text[:SUMMARY_MAX_CHARS],
        image_url=article.image_url,
    )
