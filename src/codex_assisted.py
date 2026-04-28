"""Codex-assisted no-API briefing manifest workflow."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from src.composers.pptx_builder import build_briefing_pptx
from src.config import SUMMARY_MAX_BYTES, SUMMARY_MIN_BYTES
from src.exporters.xlsx_exporter import export_briefing_xlsx
from src.schemas import ArticleSummary, BriefingResult, SlidePlan


class ManifestError(ValueError):
    """Raised when a Codex-assisted briefing manifest is invalid."""


@dataclass(frozen=True)
class CodexBriefingManifest:
    """No-API manifest prepared by Codex from user-provided briefing inputs."""

    title: str
    summaries: tuple[ArticleSummary, ...]
    slide_plans: tuple[SlidePlan, ...]


def load_manifest(path: Path) -> CodexBriefingManifest:
    """Load and validate a Codex-assisted briefing manifest."""
    raw_payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw_payload, dict):
        raise ManifestError("manifest must contain a JSON object")
    payload = cast(dict[str, Any], raw_payload)
    title = _string_value(payload.get("title"), default="Weekly Briefing")
    raw_articles = payload.get("articles")
    if not isinstance(raw_articles, list) or not raw_articles:
        raise ManifestError("manifest must include at least one article")

    summaries = tuple(
        _summary_from_payload(item, index)
        for index, item in enumerate(raw_articles, start=1)
        if isinstance(item, dict)
    )
    if len(summaries) != len(raw_articles):
        raise ManifestError("all article entries must be JSON objects")

    slide_plans = tuple(
        SlidePlan(
            article_id=summary.article_id,
            layout="title_summary_visual",
            visual_type="image" if summary.image_url else "source_thumbnail_or_chart",
        )
        for summary in summaries
    )
    return CodexBriefingManifest(
        title=title,
        summaries=summaries,
        slide_plans=slide_plans,
    )


def build_from_manifest(manifest_path: Path, output_path: Path, *, run_id: str) -> BriefingResult:
    """Build XLSX and PPTX artifacts directly from a Codex-prepared manifest."""
    manifest = load_manifest(manifest_path)
    xlsx_path = output_path.with_suffix(".xlsx")
    export_briefing_xlsx(manifest.summaries, xlsx_path)
    build_briefing_pptx(manifest.summaries, manifest.slide_plans, output_path)
    return BriefingResult(
        output_path=str(output_path),
        run_id=run_id,
        slide_count=len(manifest.summaries),
        xlsx_path=str(xlsx_path),
    )


def _summary_from_payload(payload: dict[object, object], index: int) -> ArticleSummary:
    article_id = _string_value(payload.get("article_id"), default=f"article-{index}")
    issue_id = _string_value(payload.get("issue_id"), default=f"issue-{index}")
    pdf_source = _required_any(payload, ("pdf_source", "PDF Source"))
    topic = _required_any(payload, ("topic", "주제"))
    pdf_summary = _required_any(payload, ("pdf_summary", "내용 요약"))
    title = _required_any(payload, ("article_title", "기사 제목", "title"))
    url = _required_any(payload, ("article_url", "기사 원본URL", "url"))
    source = _required_any(payload, ("article_source", "기사 출처", "source"))
    summary = _required_any(payload, ("article_summary", "기사 내용 정리", "summary"))
    conclusion = _required_any(payload, ("conclusion", "결론 및 시사점"))
    image_url = _optional_string(payload.get("image_url"))
    summary_bytes = len(summary.encode("utf-8"))
    if summary_bytes < SUMMARY_MIN_BYTES:
        raise ManifestError(f"{article_id} summary is below {SUMMARY_MIN_BYTES} bytes")
    if summary_bytes > SUMMARY_MAX_BYTES:
        raise ManifestError(f"{article_id} summary exceeds {SUMMARY_MAX_BYTES} bytes")
    return ArticleSummary(
        article_id=article_id,
        issue_id=issue_id,
        title=title,
        source=source,
        url=url,
        summary=summary,
        pdf_source=pdf_source,
        topic=topic,
        pdf_summary=pdf_summary,
        conclusion=conclusion,
        image_url=image_url,
    )


def _required_any(payload: dict[object, object], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ManifestError(f"article field is required: {' / '.join(keys)}")


def _optional_string(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _string_value(value: object, *, default: str) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else default
