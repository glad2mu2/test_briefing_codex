# DESIGN.md — Codex/OpenAI Technical Blueprint

This document describes the Codex-assisted implementation for the construction weekly briefing PPT generator.

## 1. Stack

- Language: Python 3.11+
- Package management: uv preferred
- Runtime fallback: project-local Windows `.venv\Scripts\python.exe` when global Python/uv is not on PATH
- Development agent: Codex, guided by `AGENTS.md`
- Primary runtime: Codex-assisted manifest creation plus local PPTX builder
- Optional runtime AI: OpenAI Agents SDK for specialist agent tasks, Responses API for short direct LLM calls
- Model routing: quality-first defaults, configurable through `.env`
- PDF processing: pdfplumber, pypdf fallback, pdf2image + pytesseract OCR fallback
- Web collection: httpx, beautifulsoup4, RSS feeds, and playwright for dynamic pages
- PPT generation: python-pptx
- Visual materials: matplotlib, pandas
- Korean NLP: kiwipiepy when deterministic tokenization is needed
- Retry policy: tenacity around network and API calls
- Tests: pytest, pytest-asyncio, pytest-cov, pytest-httpx, respx
- Lint/type checks: ruff, mypy

## 2. Directory Plan

```text
src/
  main.py                  # CLI entrypoint for codex_assisted and api_auto
  codex_assisted.py        # No-API manifest loader and PPTX build workflow
  orchestrator.py          # Layer 0: step ordering, persistence, failure policy
  state.py                 # Layer 0: JSON run state and transfer logs
  config.py                # Settings, model routing, constants
  schemas.py               # Shared dataclass I/O contracts
  collectors/
    pdf_collector.py       # Layer 1: upload validation, KFCC/CERIK collection
  extractors/
    pdf_text.py            # Layer 1: local PDF text extraction
    article_media.py       # Layer 1: deterministic HTML media/table extraction
  dedup/
    cosine_dedup.py        # Layer 1: deterministic issue dedup
  composers/
    pptx_builder.py        # Layer 1: PPTX assembly
  agents/
    openai_agent_runner.py # Layer 2: OpenAI Agents SDK adapter
    pdf_issue_extractor.py
    news_researcher.py
    article_summarizer.py
    fact_checker.py
  llm/
    client.py              # Layer 3: Responses API wrapper
    prompts.py             # Prompt/knowledge packet loader
    classifier.py
    layout_chooser.py

examples/                  # Example Codex-assisted manifests
prompts/                   # Knowledge packets for optional api_auto mode
data/pdfs/                 # Source PDFs; do not modify/delete existing files
data/extracted/            # Run state and extracted artifacts
data/articles/             # Article cache
data/output/               # Final PPTX output only
templates/                 # PPT templates; do not modify/delete existing files
tests/                     # Unit and integration tests
```

## 3. Primary Codex-Assisted Pipeline

The default workflow is intentionally human-in-the-loop inside Codex:

1. The user asks Codex to create a construction briefing from files in `uploads/`.
2. Codex reads PDFs and source files in the workspace.
3. Codex collects related recent domestic articles and prepares `data/articles/codex_briefing_manifest.json`.
4. The local CLI validates the manifest and builds XLSX plus PPTX under `data/output/`.

This mode does not require `OPENAI_API_KEY` and does not make local OpenAI API calls.

## 4. Optional API Automation Pipeline

The orchestrator must execute these stages in order and must not continue automatically after a stage failure:

1. PDF collection and upload validation.
2. Local PDF text extraction.
3. OpenAI specialist agent issue extraction, parallelized per PDF.
4. Direct LLM classification plus deterministic deduplication.
5. OpenAI specialist agent news research, parallelized per issue.
6. Article summarization, fact checking, and deterministic media extraction.
7. Layout choice, PPTX assembly, final metadata validation, and save to `data/output/`.

The orchestrator persists each stage to JSON so failed runs can be inspected and later resumed.

## 5. OpenAI Runtime Mapping

Layer 2 specialist agents use the OpenAI Agents SDK. The orchestrator constructs each specialist with explicit instructions and sends all necessary file paths, text snippets, URLs, and output expectations. Nested handoffs are disabled; the orchestrator directly runs the needed specialists with `asyncio.gather`.

Layer 3 direct LLM calls use the shared `src/llm/client.py` wrapper. These calls are reserved for short classification and layout decisions where a separate specialist agent is unnecessary.

Default model routing:

| Stage | Default model | Reason |
|---|---|---|
| Issue extraction | `gpt-5.5` | Highest reasoning quality |
| News research | `gpt-5.4` | Strong search and synthesis |
| Summarization | `gpt-5.4-mini` | Lower-cost short output |
| Fact checking | `gpt-5.5` | Accuracy critical |
| Classification | `gpt-5.4-mini` | Short constrained labels |
| Layout choice | `gpt-5.5` | High-quality slide planning |

All model names can be overridden in `.env`.

## 6. Data And Copyright Policy

- User PDF originals are never uploaded to OpenAI or any other external service.
- Extracted user-PDF text chunks may be sent to OpenAI only when `ALLOW_OPENAI_TEXT_UPLOAD=true`.
- Every OpenAI text transfer logs provider, purpose, source path, page numbers, and character count in run state.
- News article output must be summarized to 1,000-2,000 UTF-8 bytes including spaces and include original URL.
- Article summaries should be detailed enough for executives to understand the article after the meeting without opening every URL.
- Slides must include source name and original URL.
- Final PPTX files must be written only under `data/output/`.

## 7. Commands

Some Windows Codex environments do not have `python`, `py`, or `uv` on PATH. Verify and install Python 3.11+ and uv first:

```powershell
python --version
py --version
uv --version
```

This workspace can run through its local venv:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

For durable Windows setup, follow `python_setup_guide.md`: install official Python and enable `Add python.exe to PATH`. Keep Windows and WSL virtual environments separate.

Then run:

```powershell
uv sync --extra dev
uv run pytest -q
uv run ruff check src tests
uv run mypy src
```

Codex-assisted CLI target:

```powershell
.\.venv\Scripts\python.exe -m src.main --mode codex_assisted --manifest .\data\articles\codex_briefing_manifest.json
```

The XLSX table uses these exact columns: `PDF Source`, `주제`, `내용 요약`, `기사 제목`, `기사 원본URL`, `기사 출처`, `기사 내용 정리`, `결론 및 시사점`.

Related news collection is domestic-only and follows this source priority: 대한경제, 한국경제 부동산 RSS, 한국경제 경제 RSS, 서울경제 부동산 RSS, 서울경제 경제 RSS, 연합뉴스 최신기사 RSS, 국토일보 RSS, 네이버 뉴스. The fallback sources are used only when higher-priority sources do not contain a relevant article.

## 8. Test Policy

- Keep existing PDF validation and extraction tests.
- Add unit tests for settings/model routing, privacy gates, state persistence, summary length limits, and required slide metadata.
- Mock OpenAI and web calls in automated tests.
- Add orchestrator tests for stage ordering and "do not continue after failure" behavior.
