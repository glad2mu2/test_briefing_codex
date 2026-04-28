"""Tests for Codex-assisted manifest workflow."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.codex_assisted import ManifestError, load_manifest


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
                        "title": "공사비 이슈",
                        "source": "사용자 제공 PDF",
                        "url": "file://uploads/source.pdf",
                        "summary": "공사비 상승 부담과 제도 개선 필요성이 제기됐다.",
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
    assert manifest.slide_plans[0].article_id == "a1"


def test_load_manifest_rejects_long_summary(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "articles": [
                    {
                        "title": "긴 요약",
                        "source": "출처",
                        "url": "https://example.com",
                        "summary": "가" * 201,
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ManifestError, match="exceeds 200"):
        load_manifest(manifest_path)
