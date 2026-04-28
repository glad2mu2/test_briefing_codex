"""Layer 0 pipeline orchestrator."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, TypeVar

from src.agents.article_summarizer import summarize_article
from src.agents.fact_checker import fact_check_summary
from src.agents.news_researcher import research_news_for_issue
from src.agents.pdf_issue_extractor import extract_issues_from_pdf
from src.collectors.pdf_collector import CollectedPDF, validate_uploaded_pdf
from src.composers.pptx_builder import build_briefing_pptx
from src.config import AppSettings
from src.dedup.cosine_dedup import deduplicate_issues
from src.extractors.pdf_text import ExtractedPDF, extract_text_from_pdf
from src.llm.classifier import classify_issue
from src.llm.client import LLMClient
from src.llm.layout_chooser import choose_layout
from src.schemas import (
    Article,
    ArticleSummary,
    BriefingResult,
    FactCheckResult,
    Issue,
    SlidePlan,
)
from src.state import PipelineState, StateStore

T = TypeVar("T")
StepCallable = Callable[[], Awaitable[T]]


class PipelineStepError(RuntimeError):
    """Raised when a pipeline step fails and execution must stop."""


class WeeklyBriefingOrchestrator:
    """Coordinate the weekly briefing pipeline."""

    def __init__(
        self,
        settings: AppSettings,
        *,
        llm_client: LLMClient | None = None,
        state_store: StateStore | None = None,
    ) -> None:
        self.settings = settings
        self.llm_client = llm_client or LLMClient(settings)
        self.state_store = state_store or StateStore(settings.state_dir)

    async def run(
        self,
        *,
        upload_dir: Path,
        output_path: Path | None = None,
    ) -> BriefingResult:
        """Run the full pipeline and return final PPTX metadata."""
        run_id = make_run_id()
        state = self.state_store.create(run_id)
        self.state_store.save(state)
        resolved_output = output_path or next_output_path(self.settings.output_dir)

        pdfs = await self._run_step(
            state,
            "collect_pdfs",
            lambda: self._collect_pdfs(upload_dir),
        )
        extracted = await self._run_step(
            state,
            "extract_text",
            lambda: self._extract_text(pdfs),
        )
        issues = await self._run_step(
            state,
            "extract_issues",
            lambda: self._extract_issues(extracted, state),
        )
        classified = await self._run_step(
            state,
            "classify_and_dedup",
            lambda: self._classify_and_dedup(issues),
        )
        articles = await self._run_step(
            state,
            "research_news",
            lambda: self._research_news(classified),
        )
        summaries = await self._run_step(
            state,
            "summarize_and_fact_check",
            lambda: self._summarize_and_fact_check(articles),
        )
        slide_plans = await self._run_step(
            state,
            "choose_layouts",
            lambda: self._choose_layouts(summaries),
        )
        output = await self._run_step(
            state,
            "build_pptx",
            lambda: self._build_pptx(summaries, slide_plans, resolved_output),
        )
        return BriefingResult(
            output_path=str(output),
            run_id=run_id,
            slide_count=len(summaries),
        )

    async def _run_step(
        self,
        state: PipelineState,
        step: str,
        func: StepCallable[T],
    ) -> T:
        try:
            result = await func()
        except Exception as exc:
            self.state_store.record_failure(state, step, exc)
            raise PipelineStepError(f"{step} failed: {exc}") from exc
        self.state_store.record_step(
            state,
            step,
            {"status": "completed", "result": _state_summary(result)},
        )
        return result

    async def _collect_pdfs(self, upload_dir: Path) -> tuple[CollectedPDF, ...]:
        if not upload_dir.exists():
            raise FileNotFoundError(f"upload directory not found: {upload_dir}")
        pdfs = tuple(
            validate_uploaded_pdf(path)
            for path in sorted(upload_dir.iterdir())
            if path.is_file()
        )
        if not pdfs:
            raise PipelineStepError(f"no upload files found in {upload_dir}")
        return pdfs

    async def _extract_text(self, pdfs: tuple[CollectedPDF, ...]) -> tuple[ExtractedPDF, ...]:
        return tuple(extract_text_from_pdf(pdf.local_path) for pdf in pdfs)

    async def _extract_issues(
        self,
        extracted: tuple[ExtractedPDF, ...],
        state: PipelineState,
    ) -> tuple[Issue, ...]:
        issue_groups = await asyncio.gather(
            *(
                extract_issues_from_pdf(
                    item,
                    self.llm_client,
                    self.settings,
                    state=state,
                    state_store=self.state_store,
                )
                for item in extracted
            )
        )
        issues = tuple(issue for group in issue_groups for issue in group)
        if not issues:
            raise PipelineStepError("no issues extracted")
        return issues

    async def _classify_and_dedup(self, issues: tuple[Issue, ...]) -> tuple[Issue, ...]:
        classified = await asyncio.gather(
            *(classify_issue(issue, self.llm_client, self.settings) for issue in issues)
        )
        deduped = deduplicate_issues(tuple(classified))
        if not deduped:
            raise PipelineStepError("all issues removed by deduplication")
        return deduped

    async def _research_news(self, issues: tuple[Issue, ...]) -> tuple[Article, ...]:
        article_groups = await asyncio.gather(
            *(
                research_news_for_issue(issue, self.llm_client, self.settings)
                for issue in issues
            )
        )
        articles = tuple(article for group in article_groups for article in group)
        if not articles:
            raise PipelineStepError("no articles found")
        return articles

    async def _summarize_and_fact_check(
        self,
        articles: tuple[Article, ...],
    ) -> tuple[ArticleSummary, ...]:
        summaries = await asyncio.gather(
            *(summarize_article(article, self.llm_client, self.settings) for article in articles)
        )
        checks = await asyncio.gather(
            *(
                fact_check_summary(article, summary, self.llm_client, self.settings)
                for article, summary in zip(articles, summaries, strict=True)
            )
        )
        passed_ids = {
            check.article_id for check in checks if _fact_check_passed(check)
        }
        passed = tuple(summary for summary in summaries if summary.article_id in passed_ids)
        if not passed:
            raise PipelineStepError("no summaries passed fact check")
        return passed

    async def _choose_layouts(
        self,
        summaries: tuple[ArticleSummary, ...],
    ) -> tuple[SlidePlan, ...]:
        plans = await asyncio.gather(
            *(choose_layout(summary, self.llm_client, self.settings) for summary in summaries)
        )
        return tuple(plans)

    async def _build_pptx(
        self,
        summaries: tuple[ArticleSummary, ...],
        slide_plans: tuple[SlidePlan, ...],
        output_path: Path,
    ) -> Path:
        return build_briefing_pptx(summaries, slide_plans, output_path)


def make_run_id() -> str:
    """Create a sortable run id."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def next_output_path(output_dir: Path) -> Path:
    """Return the next available briefing output path."""
    today = datetime.now().strftime("%Y%m%d")
    output_dir.mkdir(parents=True, exist_ok=True)
    version = 1
    while True:
        candidate = output_dir / f"briefing_{today}_v{version}.pptx"
        if not candidate.exists():
            return candidate
        version += 1


def _fact_check_passed(check: FactCheckResult) -> bool:
    return check.passed


def dataclass_payload(items: tuple[object, ...]) -> list[dict[str, Any]]:
    """Return dataclass items as dictionaries for tests and future state payloads."""
    return [
        asdict(item)
        for item in items
        if is_dataclass(item) and not isinstance(item, type)
    ]


def _state_summary(value: object) -> object:
    if isinstance(value, tuple):
        items = [_item_summary(item) for item in value]
        return {
            "count": len(value),
            "items": items,
        }
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    return str(value)


def _item_summary(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    return str(value)
