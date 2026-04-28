"""News research specialist."""

from __future__ import annotations

from src.agents.openai_agent_runner import run_specialist_json
from src.config import (
    DOMESTIC_NEWS_DOMAINS,
    AppSettings,
    format_domestic_news_source_priority,
)
from src.llm.client import LLMClient
from src.schemas import Article, Issue


async def research_news_for_issue(
    issue: Issue,
    client: LLMClient,
    settings: AppSettings,
) -> tuple[Article, ...]:
    """Find trusted articles for one issue using an OpenAI specialist prompt."""
    source_priority = format_domestic_news_source_priority()
    allowed_domains = ", ".join(DOMESTIC_NEWS_DOMAINS)
    instructions = (
        "You research recent Korean domestic construction-industry news for a briefing. "
        "Use only Korean domestic news sources. Follow this source priority exactly, "
        "moving to a lower tier only when no relevant article exists in higher tiers:\n"
        f"{source_priority}\n"
        f"Allowed domains: {allowed_domains}. "
        "Use Naver News only as a fallback discovery source; when possible return the "
        "original press URL instead of a Naver aggregator URL. Return only JSON: "
        "{\"articles\": [{\"id\": string, \"title\": string, \"source\": string, "
        "\"url\": string, \"published_at\": string, \"body\": string, "
        "\"image_url\": string|null}]}. Do not invent URLs."
    )
    payload = await run_specialist_json(
        name="news-researcher",
        model=settings.models.news_research,
        instructions=instructions,
        user_input=(
            f"Issue title: {issue.title}\n"
            f"Description: {issue.description}\n"
            f"Keywords: {', '.join(issue.keywords)}"
        ),
        schema_name="news research",
        settings=settings,
        fallback_client=client,
    )
    articles = payload.get("articles", [])
    if not isinstance(articles, list):
        return ()
    return tuple(
        _article_from_payload(item, issue_id=issue.issue_id)
        for item in articles
        if isinstance(item, dict)
    )


def _article_from_payload(payload: dict[object, object], *, issue_id: str) -> Article:
    article_id = _string_value(payload.get("id"), default=f"{issue_id}-article")
    title = _string_value(payload.get("title"), default="Untitled article")
    source = _string_value(payload.get("source"), default="Unknown")
    url = _string_value(payload.get("url"), default="")
    published_at = _optional_string(payload.get("published_at"))
    body = _string_value(payload.get("body"), default="")
    image_url = _optional_string(payload.get("image_url"))
    return Article(
        article_id=article_id,
        issue_id=issue_id,
        title=title,
        source=source,
        url=url,
        published_at=published_at,
        body=body,
        image_url=image_url,
    )


def _optional_string(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _string_value(value: object, *, default: str) -> str:
    return value if isinstance(value, str) and value else default
