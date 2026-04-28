# Weekly Briefing Agent

Construction-industry weekly briefing PPT generator.

This repository is now oriented around Codex for development and OpenAI APIs for runtime AI.

## Setup

Install Python 3.11+ and uv. On Windows, first verify whether they are already on PATH:

```powershell
python --version
py --version
uv --version
```

Install dependencies:

```powershell
uv sync --extra dev
```

Copy `.env.example` to `.env` and set:

```text
OPENAI_API_KEY=...
ALLOW_OPENAI_TEXT_UPLOAD=true
```

`ALLOW_OPENAI_TEXT_UPLOAD=true` is required for AI stages that send extracted user-PDF text chunks to OpenAI. Original PDF files are not uploaded.

## Test

```powershell
uv run pytest -q
uv run ruff check src tests
uv run mypy src
```

## Run

Put uploaded PDFs under `uploads/`, then run:

```powershell
uv run python -m src.main --upload-dir .\uploads
```

The generated PPTX is written under `data/output/`. Pipeline run state and transfer audit logs are written under `data/extracted/{run_id}/state.json`.

## Key Files

- `AGENTS.md`: Codex project instructions.
- `DESIGN.md`: OpenAI runtime architecture.
- `ROADMAP.md`: remaining implementation and product decisions.
- `src/orchestrator.py`: pipeline coordinator.
- `src/llm/client.py`: Responses API wrapper and privacy gate.
- `src/agents/`: OpenAI specialist agents.
