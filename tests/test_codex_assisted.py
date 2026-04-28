"""Tests for Codex-assisted manifest workflow."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.codex_assisted import ManifestError, load_manifest
from src.config import SUMMARY_MAX_BYTES, SUMMARY_MIN_BYTES


def test_load_manifest_validates_required_fields(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "title": "건설업 주간 브리핑",
                "articles": [
                    {
                        "article_id": "a1",
                        "issue_id": "i1",
                        "pdf_source": "사용자 제공 PDF",
                        "topic": "공사비",
                        "pdf_summary": "공사비 상승 부담이 PDF 주요 이슈로 정리됐다.",
                        "article_title": "공사비 이슈",
                        "article_source": "사용자 제공 PDF",
                        "article_url": "file://uploads/source.pdf",
                        "article_summary": "공사비 상승 부담과 제도 개선 필요성이 제기됐다. " * 20,
                        "conclusion": "발주 조건과 물가 반영 기준 점검이 필요하다.",
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    manifest = load_manifest(manifest_path)

    assert manifest.title == "건설업 주간 브리핑"
    assert len(manifest.summaries) == 1
    assert manifest.summaries[0].source == "사용자 제공 PDF"
    assert manifest.summaries[0].topic == "공사비"
    assert manifest.slide_plans[0].article_id == "a1"


def test_load_manifest_accepts_requested_xlsx_column_names(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "articles": [
                    {
                        "PDF Source": "CERIK 건설동향브리핑",
                        "주제": "시장·정책",
                        "내용 요약": "PDF에서 주택 공급 정책 이슈가 확인됐다.",
                        "기사 제목": "관련 최신 기사",
                        "기사 원본URL": "https://example.com/news",
                        "기사 출처": "예시 언론",
                        "기사 내용 정리": (
                            "주택 공급 확대와 인허가 간소화 논의가 이어지고 있다. " * 20
                        ),
                        "결론 및 시사점": "공급 정책은 제도 개선과 투자 유인이 함께 필요하다.",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    manifest = load_manifest(manifest_path)

    assert manifest.summaries[0].pdf_source == "CERIK 건설동향브리핑"
    assert manifest.summaries[0].title == "관련 최신 기사"
    assert manifest.summaries[0].conclusion == "공급 정책은 제도 개선과 투자 유인이 함께 필요하다."


def test_load_manifest_rejects_short_summary(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "articles": [
                    {
                        "pdf_source": "PDF",
                        "topic": "주제",
                        "pdf_summary": "내용 요약",
                        "article_title": "긴 요약",
                        "article_source": "출처",
                        "article_url": "https://example.com",
                        "article_summary": "짧은 요약",
                        "conclusion": "시사점",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ManifestError, match=f"below {SUMMARY_MIN_BYTES}"):
        load_manifest(manifest_path)


def test_load_manifest_rejects_long_summary(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "articles": [
                    {
                        "pdf_source": "PDF",
                        "topic": "주제",
                        "pdf_summary": "내용 요약",
                        "article_title": "긴 요약",
                        "article_source": "출처",
                        "article_url": "https://example.com",
                        "article_summary": "가" * SUMMARY_MAX_BYTES,
                        "conclusion": "시사점",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ManifestError, match=f"exceeds {SUMMARY_MAX_BYTES}"):
        load_manifest(manifest_path)
