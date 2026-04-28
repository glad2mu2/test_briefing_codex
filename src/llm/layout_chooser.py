"""Slide layout selection via direct OpenAI Responses API calls."""

from __future__ import annotations

from src.config import AppSettings
from src.llm.client import LLMClient
from src.schemas import ArticleSummary, SlidePlan


async def choose_layout(
    summary: ArticleSummary,
    client: LLMClient,
    settings: AppSettings,
) -> SlidePlan:
    """Choose a slide layout for one article summary."""
    instructions = (
        "You choose PPT slide layouts for Korean executive briefings. "
        "Return only JSON: {\"layout\": string, \"visual_type\": string, "
        "\"speaker_note\": string}. Use compact professional layouts."
    )
    payload = await client.complete_json(
        model=settings.models.layout,
        instructions=instructions,
        user_input=(
            f"Title: {summary.title}\n"
            f"Source: {summary.source}\n"
            f"Summary: {summary.summary}\n"
            f"Image URL: {summary.image_url or ''}"
        ),
        schema_name="layout choice",
    )
    layout = _string_value(payload.get("layout"), default="title_summary_visual")
    visual_type = _string_value(payload.get("visual_type"), default="none")
    speaker_note = _string_value(payload.get("speaker_note"), default="")
    return SlidePlan(
        article_id=summary.article_id,
        layout=layout,
        visual_type=visual_type,
        speaker_note=speaker_note,
    )


def _string_value(value: object, *, default: str) -> str:
    return value if isinstance(value, str) and value else default
