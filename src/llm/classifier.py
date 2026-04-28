"""Issue classification via direct OpenAI Responses API calls."""

from __future__ import annotations

from src.config import ISSUE_CATEGORIES, AppSettings
from src.llm.client import LLMClient
from src.schemas import Issue


async def classify_issue(
    issue: Issue,
    client: LLMClient,
    settings: AppSettings,
) -> Issue:
    """Classify one issue into configured construction categories."""
    instructions = (
        "You classify Korean construction-industry issues. "
        "Return only JSON: {\"categories\": [..]}. "
        f"Allowed categories: {', '.join(ISSUE_CATEGORIES)}."
    )
    payload = await client.complete_json(
        model=settings.models.classification,
        instructions=instructions,
        user_input=f"Title: {issue.title}\nDescription: {issue.description}",
        schema_name="issue classification",
    )
    categories = _categories_from_payload(payload.get("categories"))
    return Issue(
        issue_id=issue.issue_id,
        title=issue.title,
        description=issue.description,
        keywords=issue.keywords,
        categories=categories,
        source_path=issue.source_path,
        page_numbers=issue.page_numbers,
    )


def _categories_from_payload(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(
        category
        for category in value
        if isinstance(category, str) and category in ISSUE_CATEGORIES
    )
