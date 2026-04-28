"""Tests for orchestrator failure policy."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.config import load_settings
from src.orchestrator import PipelineStepError, WeeklyBriefingOrchestrator
from src.state import StateStore


class FailingOrchestrator(WeeklyBriefingOrchestrator):
    def __init__(self, state_dir: Path, output_dir: Path) -> None:
        settings = load_settings(
            {
                "STATE_DIR": str(state_dir),
                "OUTPUT_DIR": str(output_dir),
                "USE_OPENAI_AGENTS_SDK": "false",
            }
        )
        super().__init__(settings, state_store=StateStore(state_dir))
        self.calls: list[str] = []

    async def _collect_pdfs(self, upload_dir: Path) -> tuple[object, ...]:
        self.calls.append("collect")
        raise RuntimeError("boom")

    async def _extract_text(self, pdfs: tuple[object, ...]) -> tuple[object, ...]:
        self.calls.append("extract")
        return ()


@pytest.mark.asyncio
async def test_orchestrator_stops_after_step_failure(tmp_path: Path) -> None:
    orchestrator = FailingOrchestrator(
        state_dir=tmp_path / "state",
        output_dir=tmp_path / "data" / "output",
    )

    with pytest.raises(PipelineStepError, match="collect_pdfs failed"):
        await orchestrator.run(upload_dir=tmp_path)

    assert orchestrator.calls == ["collect"]
