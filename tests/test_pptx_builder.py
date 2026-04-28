"""Tests for PPTX builder validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.composers.pptx_builder import PPTXBuildError, build_briefing_pptx
from src.schemas import ArticleSummary, SlidePlan


def test_pptx_builder_rejects_missing_source(tmp_path: Path) -> None:
    summary = ArticleSummary(
        article_id="a1",
        issue_id="i1",
        title="제목",
        source="",
        url="https://example.com",
        summary="요약",
    )
    output = tmp_path / "data" / "output" / "briefing.pptx"

    with pytest.raises(PPTXBuildError, match="source and url required"):
        build_briefing_pptx((summary,), (), output)


def test_pptx_builder_rejects_output_outside_data_output(tmp_path: Path) -> None:
    summary = ArticleSummary(
        article_id="a1",
        issue_id="i1",
        title="제목",
        source="대한경제",
        url="https://example.com",
        summary="요약",
    )
    plan = SlidePlan(article_id="a1", layout="title_summary_visual", visual_type="none")

    with pytest.raises(PPTXBuildError, match="data/output"):
        build_briefing_pptx((summary,), (plan,), tmp_path / "briefing.pptx")
