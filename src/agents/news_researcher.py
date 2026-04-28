"""News research specialist."""

from __future__ import annotations

from src.agents.openai_agent_runner import run_specialist_json
from src.config import AppSettings, SOURCE_WHITELIST_TIER_1, SOURCE_WHITELIST_TIER_2
from src.llm.client import LLMClient
from src.schemas import Article, Issue


async def research_news_for_issue(
    issue: Issue,
    client: LLMClient,
    settings: AppSettings,
) -> tuple[Article, ...]:
    """Find trusted articles for one issue using an OpenAI specialist prompt."""
    trusted_sources = ", ".join(
        item["name"] for item in SOURCE_WHITELIST_TIER_1 + SOURCE_WHITELIST_TIER_2
    )
    instructions = (
        "You research recent Korean construction-industry news for a briefing. "
        "Prefer trusted sources in this order: "
        f"{trusted_sources}. Return only JSON: "
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
