"""OpenAI Responses API wrapper used by direct LLM stages."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

from src.config import AppSettings, OPENAI_PROVIDER_NAME
from src.state import DataTransferLog, PipelineState, StateStore, utc_now


class LLMError(RuntimeError):
    """Base error raised by LLM integration."""


class DataTransferNotAllowedError(LLMError):
    """Raised when extracted PDF text transfer is disabled."""


class InvalidLLMJSONError(LLMError):
    """Raised when a model response is not valid JSON."""


class ResponsesClientProtocol(Protocol):
    """Subset of the OpenAI async client used by this project."""

    responses: Any


@dataclass(frozen=True)
class TextTransferRequest:
    """Metadata required before sending extracted PDF text to OpenAI."""

    purpose: str
    source_path: Path
    page_numbers: tuple[int, ...]
    text: str


class LLMClient:
    """Small wrapper around the OpenAI Responses API.

    A client can be injected in tests. When no client is provided, the OpenAI
    SDK is imported lazily so non-AI tests can import this module without
    network or credential setup.
    """

    def __init__(
        self,
        settings: AppSettings,
        client: ResponsesClientProtocol | None = None,
    ) -> None:
        self.settings = settings
        self._client = client

    async def complete_json(
        self,
        *,
        model: str,
        instructions: str,
        user_input: str,
        schema_name: str,
    ) -> dict[str, Any]:
        """Generate a JSON object from the Responses API.

        Args:
            model: OpenAI model id.
            instructions: System-level guidance.
            user_input: User/task input.
            schema_name: Friendly name used in error messages.

        Returns:
            Parsed JSON object.

        Raises:
            InvalidLLMJSONError: If the response cannot be parsed as a JSON object.
        """
        client = self._get_client()
        response = await client.responses.create(
            model=model,
            instructions=instructions,
            input=user_input,
        )
        output_text = _extract_output_text(response)
        try:
            payload = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise InvalidLLMJSONError(
                f"{schema_name} response was not valid JSON: {output_text[:200]}"
            ) from exc
        if not isinstance(payload, dict):
            raise InvalidLLMJSONError(f"{schema_name} response must be a JSON object")
        return cast(dict[str, Any], payload)

    def require_text_transfer_allowed(
        self,
        request: TextTransferRequest,
        state: PipelineState | None = None,
        state_store: StateStore | None = None,
    ) -> DataTransferLog:
        """Validate and audit extracted-text transfer to OpenAI.

        Args:
            request: Transfer metadata and text.
            state: Optional pipeline state to persist the audit log into.
            state_store: Optional state store used when state is provided.

        Returns:
            DataTransferLog representing the approved transfer.

        Raises:
            DataTransferNotAllowedError: If environment policy disallows transfer.
        """
        if not self.settings.allow_openai_text_upload:
            raise DataTransferNotAllowedError(
                "extracted PDF text transfer is disabled; set "
                "ALLOW_OPENAI_TEXT_UPLOAD=true to run AI stages"
            )
        transfer = DataTransferLog(
            provider=OPENAI_PROVIDER_NAME,
            purpose=request.purpose,
            source_path=str(request.source_path),
            page_numbers=request.page_numbers,
            char_count=len(request.text),
            created_at=utc_now(),
        )
        if state is not None and state_store is not None:
            state_store.record_transfer(state, transfer)
        return transfer

    def _get_client(self) -> ResponsesClientProtocol:
        if self._client is not None:
            return self._client
        if self.settings.openai_api_key is None:
            raise LLMError("OPENAI_API_KEY is required for OpenAI runtime calls")
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise LLMError("openai package is not installed") from exc
        self._client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        return self._client


def _extract_output_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str):
        return output_text
    if isinstance(response, dict) and isinstance(response.get("output_text"), str):
        return str(response["output_text"])
    return str(response)
