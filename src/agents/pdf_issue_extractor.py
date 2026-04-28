"""PDF issue extraction specialist."""

from __future__ import annotations

from src.agents.openai_agent_runner import run_specialist_json
from src.config import AppSettings
from src.extractors.pdf_text import ExtractedPDF
from src.llm.client import LLMClient, TextTransferRequest
from src.schemas import Issue
from src.state import PipelineState, StateStore


async def extract_issues_from_pdf(
    extracted_pdf: ExtractedPDF,
    client: LLMClient,
    settings: AppSettings,
    state: PipelineState | None = None,
    state_store: StateStore | None = None,
) -> tuple[Issue, ...]:
    """Extract construction issues from one locally extracted PDF."""
    text = "\n\n".join(
        f"[page {page.page_number}]\n{page.text}" for page in extracted_pdf.pages
    )
    page_numbers = tuple(page.page_number for page in extracted_pdf.pages)
    client.require_text_transfer_allowed(
        TextTransferRequest(
            purpose="pdf_issue_extraction",
            source_path=extracted_pdf.source_path,
            page_numbers=page_numbers,
            text=text,
        ),
        state=state,
        state_store=state_store,
    )

    instructions = (
        "You extract weekly briefing issues from Korean construction PDFs. "
        "Return only JSON: {\"issues\": [{\"id\": string, \"title\": string, "
        "\"description\": string, \"keywords\": [string], "
        "\"page_numbers\": [integer]}]}. Focus on management-relevant issues."
    )
    payload = await run_specialist_json(
        name="pdf-issue-extractor",
        model=settings.models.issue_extraction,
        instructions=instructions,
        user_input=text,
        schema_name="pdf issue extraction",
        settings=settings,
        fallback_client=client,
    )
    issues = payload.get("issues", [])
    if not isinstance(issues, list):
        return ()
    return tuple(
        _issue_from_payload(item, source_path=str(extracted_pdf.source_path))
        for item in issues
        if isinstance(item, dict)
    )


def _issue_from_payload(payload: dict[object, object], *, source_path: str) -> Issue:
    issue_id = _string_value(payload.get("id"), default="issue")
    title = _string_value(payload.get("title"), default="Untitled issue")
    description = _string_value(payload.get("description"), default="")
    keywords = _string_tuple(payload.get("keywords"))
    page_numbers = _int_tuple(payload.get("page_numbers"))
    return Issue(
        issue_id=issue_id,
        title=title,
        description=description,
        keywords=keywords,
        source_path=source_path,
        page_numbers=page_numbers,
    )


def _string_value(value: object, *, default: str) -> str:
    return value if isinstance(value, str) and value else default


def _string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str))


def _int_tuple(value: object) -> tuple[int, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, int))
