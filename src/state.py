"""JSON persistence for orchestrator run state."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast


@dataclass(frozen=True)
class DataTransferLog:
    """Audit record for text sent to an external AI provider."""

    provider: str
    purpose: str
    source_path: str
    page_numbers: tuple[int, ...]
    char_count: int
    created_at: str


@dataclass
class PipelineState:
    """Mutable run state persisted after each pipeline stage."""

    run_id: str
    created_at: str
    updated_at: str
    steps: dict[str, Any] = field(default_factory=dict)
    failures: list[dict[str, Any]] = field(default_factory=list)
    data_transfers: list[DataTransferLog] = field(default_factory=list)


class StateStore:
    """Persist and load pipeline state under a state directory."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def create(self, run_id: str) -> PipelineState:
        """Create a fresh state object for a run."""
        now = utc_now()
        return PipelineState(run_id=run_id, created_at=now, updated_at=now)

    def save(self, state: PipelineState) -> Path:
        """Persist state and return the JSON path."""
        state.updated_at = utc_now()
        path = self.path_for(state.run_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(_to_jsonable(state), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def load(self, run_id: str) -> PipelineState:
        """Load state for an existing run."""
        raw_payload = json.loads(self.path_for(run_id).read_text(encoding="utf-8"))
        if not isinstance(raw_payload, dict):
            raise ValueError(f"state file for {run_id} must contain a JSON object")
        payload = cast(dict[str, Any], raw_payload)
        transfers = tuple(
            DataTransferLog(
                provider=str(item["provider"]),
                purpose=str(item["purpose"]),
                source_path=str(item["source_path"]),
                page_numbers=_int_tuple(item["page_numbers"]),
                char_count=int(item["char_count"]),
                created_at=str(item["created_at"]),
            )
            for item in payload.get("data_transfers", [])
            if isinstance(item, dict)
        )
        state = PipelineState(
            run_id=payload["run_id"],
            created_at=payload["created_at"],
            updated_at=payload["updated_at"],
            steps=dict(payload.get("steps", {})),
            failures=list(payload.get("failures", [])),
            data_transfers=list(transfers),
        )
        return state

    def path_for(self, run_id: str) -> Path:
        """Return the JSON state path for a run id."""
        return self.root / run_id / "state.json"

    def record_step(
        self,
        state: PipelineState,
        step: str,
        payload: dict[str, Any],
    ) -> None:
        """Record a completed step and persist state."""
        state.steps[step] = payload
        self.save(state)

    def record_failure(
        self,
        state: PipelineState,
        step: str,
        error: Exception,
    ) -> None:
        """Record a failed step and persist state."""
        state.failures.append(
            {
                "step": step,
                "error_type": type(error).__name__,
                "message": str(error),
                "created_at": utc_now(),
            }
        )
        self.save(state)

    def record_transfer(
        self,
        state: PipelineState,
        transfer: DataTransferLog,
    ) -> None:
        """Record an OpenAI text transfer audit entry."""
        state.data_transfers.append(transfer)
        self.save(state)


def utc_now() -> str:
    """Return a timezone-aware UTC timestamp as ISO-8601 text."""
    return datetime.now(tz=timezone.utc).isoformat()


def _to_jsonable(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        return _to_jsonable(asdict(value))
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    return value


def _int_tuple(value: object) -> tuple[int, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, int))
