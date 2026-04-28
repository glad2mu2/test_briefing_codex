"""Article summary fact-checking specialist."""

from __future__ import annotations

from src.agents.openai_agent_runner import run_specialist_json
from src.config import AppSettings
from src.llm.client import LLMClient
from src.schemas import Article, ArticleSummary, FactCheckResult


async def fact_check_summary(
    article: Article,
    summary: ArticleSummary,
    client: LLMClient,
    settings: AppSettings,
) -> FactCheckResult:
    """Check a summary against its source article body."""
    instructions = (
        "You fact-check a Korean news summary against the source text. "
        "Return only JSON: {\"passed\": boolean, \"reasons\": [string]}. "
        "Fail if the summary adds unsupported claims or omits source attribution."
    )
    payload = await run_specialist_json(
        name="fact-checker",
        model=settings.models.fact_check,
        instructions=instructions,
        user_input=(
            f"Article title: {article.title}\n"
            f"URL: {article.url}\n"
            f"Source body:\n{article.body}\n\n"
            f"Summary:\n{summary.summary}"
        ),
        schema_name="fact check",
        settings=settings,
        fallback_client=client,
    )
    reasons = _string_tuple(payload.get("reasons"))
    return FactCheckResult(
        article_id=article.article_id,
        passed=bool(payload.get("passed", False)),
        reasons=reasons,
    )


def _string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str))
