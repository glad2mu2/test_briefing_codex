"""Tests for pipeline state persistence."""

from __future__ import annotations

from pathlib import Path

from src.state import DataTransferLog, StateStore


def test_state_store_round_trip(tmp_path: Path) -> None:
    store = StateStore(tmp_path)
    state = store.create("run-1")
    store.record_step(state, "collect_pdfs", {"status": "completed"})
    store.record_transfer(
        state,
        DataTransferLog(
            provider="openai",
            purpose="pdf_issue_extraction",
            source_path="sample.pdf",
            page_numbers=(1, 2),
            char_count=123,
            created_at="2026-04-28T00:00:00+00:00",
        ),
    )

    loaded = store.load("run-1")

    assert loaded.run_id == "run-1"
    assert loaded.steps["collect_pdfs"]["status"] == "completed"
    assert loaded.data_transfers[0].provider == "openai"
    assert loaded.data_transfers[0].page_numbers == (1, 2)
