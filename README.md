# Weekly Briefing Agent

Construction-industry weekly briefing PPT generator.

This repository is oriented around Codex-assisted briefing creation by default.
OpenAI API automation remains optional.

## Setup

This workspace currently has a project-local Windows virtual environment:

```powershell
.\.venv\Scripts\python.exe --version
```

Use that path for project commands when `python`, `py`, `uv`, or `pip` are not on PATH.

For a clean Windows setup, install official Python 3.11+ or 3.12+ from python.org and check **Add python.exe to PATH** during installation. If Windows opens Microsoft Store when typing `python`, turn off the Python App Execution Alias in Windows Settings.

After Python is available on PATH, install uv if desired:

```powershell
python --version
py --version
uv --version
```

Install or refresh dependencies:

```powershell
uv sync --extra dev
```

If uv is unavailable but `.venv` already works, use the existing `.venv` directly.

Copy `.env.example` to `.env`. The default mode does not need an API key:

```text
BRIEFING_RUN_MODE=codex_assisted
USE_OPENAI_AGENTS_SDK=false
ALLOW_OPENAI_TEXT_UPLOAD=false
```

Only `api_auto` mode needs `OPENAI_API_KEY`. That mode may incur API charges.

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

When uv is installed:

```powershell
uv run ruff check src tests
uv run mypy src
```

## Run

For the no-API Codex-assisted workflow, ask Codex to create a manifest from your PDFs, then run:

```powershell
.\.venv\Scripts\python.exe -m src.main --mode codex_assisted --manifest .\data\articles\codex_briefing_manifest.json
```

The generated PPTX is written under `data/output/`. Pipeline run state and transfer audit logs are written under `data/extracted/{run_id}/state.json`.

See `CODEX_WORKFLOW.md` for the exact Codex request pattern and manifest format.

## Windows Python Notes

See `python_setup_guide.md` for the longer setup guide. The important rule is: Windows `.venv` runs in Windows PowerShell/CMD, and WSL `.venv` runs inside WSL. Do not mix virtual environments across operating systems.

## Key Files

- `AGENTS.md`: Codex project instructions.
- `DESIGN.md`: OpenAI runtime architecture.
- `ROADMAP.md`: remaining implementation and product decisions.
- `CODEX_WORKFLOW.md`: no-API Codex-assisted PPT workflow.
- `src/orchestrator.py`: pipeline coordinator.
- `src/llm/client.py`: Responses API wrapper and privacy gate.
- `src/agents/`: OpenAI specialist agents.
