# ROADMAP.md — Codex/OpenAI Migration

This document tracks unresolved decisions and implementation work after the Codex/OpenAI migration decision.

## A. Current Decisions

- Delivery model: Codex-assisted PPT generation first.
- Development and briefing operator: Codex, guided by `AGENTS.md` and `CODEX_WORKFLOW.md`.
- Default runtime provider: none. Local code builds PPTX from a manifest without API calls.
- Optional runtime provider: OpenAI API in `api_auto` mode.
- Privacy policy: original PDF files stay local; extracted text chunks may be sent to OpenAI only in `api_auto` when `ALLOW_OPENAI_TEXT_UPLOAD=true`.

## B. Implementation Priority

1. Codex-assisted manifest workflow and PPTX builder.
2. Local runtime setup with Python/uv or project `.venv`.
3. Documentation for user-to-Codex briefing requests.
4. Optional Layer 0 orchestrator, state persistence, and CLI entrypoint for `api_auto`.
5. Optional Layer 3 OpenAI client wrapper, prompt loader, and structured dataclass schemas.
6. Optional Layer 2 specialist agents:
   - `pdf_issue_extractor`
   - `news_researcher`
   - `article_summarizer`
   - `fact_checker`
7. Remaining deterministic Layer 1 modules:
   - `dedup/cosine_dedup.py`
   - `extractors/article_media.py`
   - `composers/pptx_builder.py`
8. Remote PDF collection:
   - KFCC via httpx
   - CERIK via Playwright
9. End-to-end acceptance run with sample PDFs and generated PPTX.

## C. Product Decisions Still Deferred

- Web UI versus CLI-only delivery after backend validation.
- Slide preview, direct editing, exclusion, and reordering workflow.
- KPI measurement for MAU and satisfaction score.
- Team/user permission model.
- English article inclusion and translation policy.
- Total slide cap enforcement beyond the 10-15 slide recommendation.
- Historical briefing storage and week-over-week comparison.

## D. Technical Decisions To Tune After MVP

- Issue dedup threshold, currently `0.85`.
- OCR trigger threshold for scanned or garbled pages.
- Chart generation rules by article/issue type.
- Font/template strategy for Korean PPT output.
- CI setup for Playwright dependencies.
- Cache retention automation for PDFs, articles, and generated PPTX.
