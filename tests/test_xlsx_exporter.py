"""Tests for XLSX export."""

from __future__ import annotations

from pathlib import Path

from openpyxl import load_workbook

from src.exporters.xlsx_exporter import XLSX_COLUMNS, export_briefing_xlsx
from src.schemas import ArticleSummary


def test_export_briefing_xlsx_writes_requested_columns(tmp_path: Path) -> None:
    output = tmp_path / "briefing.xlsx"
    row = ArticleSummary(
        article_id="a1",
        issue_id="i1",
        title="기사 제목",
        source="기사 출처",
        url="https://example.com",
        summary="기사 내용 정리",
        pdf_source="PDF Source",
        topic="주제",
        pdf_summary="내용 요약",
        conclusion="결론 및 시사점",
    )

    export_briefing_xlsx((row,), output)

    workbook = load_workbook(output)
    worksheet = workbook.active
    assert [cell.value for cell in worksheet[1]] == list(XLSX_COLUMNS)
    assert worksheet["A2"].value == "PDF Source"
    assert worksheet["D2"].value == "기사 제목"
    assert worksheet["H2"].value == "결론 및 시사점"
    assert worksheet.row_dimensions[2].height == 120
