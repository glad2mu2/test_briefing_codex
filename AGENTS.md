# AGENTS.md

Codex project guidance for the construction weekly briefing generator.

## Project Identity

This repository builds a Python 3.11+ backend that analyzes construction-industry PDFs and related news, then generates a weekly briefing `.pptx`.

Primary users are construction-company planning or management-support staff who prepare weekly executive briefing decks.

The implementation priority is Codex-assisted PPT generation. Web UI, slide preview, direct editing, and slide ordering remain deferred until the delivery model is decided.

## Source Of Truth

Use this order when requirements conflict:

1. `건설업 주간 브리핑 PPT 자동 생성 솔루션_기능명세서_2026-04-27.md`
2. `DESIGN.md`
3. `ROADMAP.md`
4. Source code and tests

`CLAUDE.md` is legacy context only. Do not add new Claude-specific runtime design there.

## Runtime Direction

- Codex is the development agent and the primary briefing operator.
- Primary mode is `codex_assisted`: Codex reads files and prepares a manifest; local code builds PPTX with no API calls.
- Optional mode is `api_auto`: OpenAI APIs run specialist tasks automatically.
- Do not add Anthropic or Claude Code runtime dependencies unless the user explicitly reopens provider support.
- Keep the orchestrator as Python code. It owns step ordering, persistence, metrics, and failure policy.
- Use specialist OpenAI agents only where isolation or parallelism is valuable: PDF issue extraction, news research, article summarization, and fact checking.
- Do not use nested handoffs for this project. The orchestrator runs specialist agents directly and may call them in parallel with `asyncio.gather`.

## Security, Copyright, And Data Rules

- Never hardcode API keys or credentials. Use `.env` or environment variables.
- Never upload original user PDF files to external services.
- In `codex_assisted` mode, do not require `OPENAI_API_KEY`.
- Extracted text chunks from user PDFs may be sent to OpenAI only when `ALLOW_OPENAI_TEXT_UPLOAD=true`.
- When text is sent to OpenAI, log and persist provider, purpose, source path, page numbers, and character count.
- Do not copy full news article bodies into generated output. Store only local cache needed for processing; slides must use a detailed executive summary of 1,000-2,000 UTF-8 bytes including spaces plus original URL.
- Every slide must include source name and original URL.
- The Codex-assisted manifest must also produce an XLSX table with: `PDF Source`, `주제`, `내용 요약`, `기사 제목`, `기사 원본URL`, `기사 출처`, `기사 내용 정리`, `결론 및 시사점`.
- PPT slides are based on article fields, not raw PDF issue text alone. Include article title, source, article summary, conclusion/implication, and article image when available.
- Related article collection must use Korean domestic articles only. Search in this order: 대한경제, 한국경제 부동산 RSS, 한국경제 경제 RSS, 서울경제 부동산 RSS, 서울경제 경제 RSS, then fallback to 연합뉴스 최신기사 RSS, 국토일보 RSS, and 네이버 뉴스.
- Do not insert article images unless source and usage are traceable. Prefer thumbnails with attribution or generated charts.
- Generated PPT files must be written under `data/output/`.
- Do not modify or delete files under `templates/` or `data/pdfs/`; adding new files is allowed when needed.

## Setup And Commands

Local PATH on some Windows Codex machines may not include `python`, `py`, `uv`, or `pip`. Verify first:

```powershell
python --version
py --version
uv --version
```

For this workspace, prefer the project-local Windows virtualenv when available:

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pytest -q
```

If Python is missing for a new Windows project, use the official Python installer and enable `Add python.exe to PATH`. If Microsoft Store opens when typing `python`, disable the Python App Execution Alias in Windows Settings. Use `python_setup_guide.md` as the detailed reference.

When uv is installed and on PATH, run:

```powershell
uv sync --extra dev
uv run pytest -q
uv run ruff check src tests
uv run mypy src
```

No-API Codex-assisted CLI target:

```powershell
.\.venv\Scripts\python.exe -m src.main --mode codex_assisted --manifest .\data\articles\codex_briefing_manifest.json
```

If the `.venv` Python reports a uv trampoline permission error, rerun the command with elevated permissions in Codex or recreate the venv from a normal Windows Python install.

Set `OPENAI_API_KEY` and `ALLOW_OPENAI_TEXT_UPLOAD=true` only before running `api_auto` against uploaded PDFs.

## Code Style

- Python modules use `snake_case.py`.
- All public functions need type hints.
- Prefer dataclasses or typed structures for pipeline state and I/O.
- Use Google-style docstrings for non-trivial public functions.
- Use `logging`, not `print()`, including CLI status output.
- Use `async/await` for I/O-bound collection and LLM calls.
- Mock all external API and network calls in tests.
- Keep changes narrowly scoped and preserve existing Layer 1 behavior unless the task requires otherwise.

## Pipeline Contract

The weekly briefing pipeline must preserve this order:

1. Collect PDFs and validate uploads.
2. Extract text locally.
3. Extract construction issues with OpenAI specialist agents.
4. Classify issues and deduplicate.
5. Research trusted domestic news sources in the configured priority order.
6. Summarize, fact-check, and extract or generate visuals.
7. Choose slide layouts, build PPTX, validate metadata, and save output.

If a stage fails, do not automatically continue. Persist the failure and return a clear error so the user can decide how to proceed.
