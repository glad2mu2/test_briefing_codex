"""Shared dataclass schemas for pipeline inputs and outputs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Issue:
    """Construction issue extracted from one or more PDFs."""

    issue_id: str
    title: str
    description: str
    keywords: tuple[str, ...]
    categories: tuple[str, ...] = ()
    source_path: str | None = None
    page_numbers: tuple[int, ...] = ()


@dataclass(frozen=True)
class Article:
    """News article metadata and optional processing body."""

    article_id: str
    issue_id: str
    title: str
    source: str
    url: str
    published_at: str | None = None
    body: str = ""
    image_url: str | None = None


@dataclass(frozen=True)
class ArticleSummary:
    """Slide-ready summary with required attribution metadata."""

    article_id: str
    issue_id: str
    title: str
    source: str
    url: str
    summary: str
    pdf_source: str = ""
    topic: str = ""
    pdf_summary: str = ""
    conclusion: str = ""
    image_url: str | None = None


@dataclass(frozen=True)
class FactCheckResult:
    """Fact-check result for one article summary."""

    article_id: str
    passed: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class SlidePlan:
    """Layout choice for one slide."""

    article_id: str
    layout: str
    visual_type: str
    speaker_note: str = ""


@dataclass(frozen=True)
class BriefingResult:
    """Final orchestrator result."""

    output_path: str
    run_id: str
    slide_count: int
    xlsx_path: str | None = None
