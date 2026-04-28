"""Adapter for running OpenAI Agents SDK specialists."""

from __future__ import annotations

import json
from typing import Any, cast

from src.config import AppSettings
from src.llm.client import InvalidLLMJSONError, LLMClient


class AgentRuntimeError(RuntimeError):
    """Raised when the OpenAI Agents SDK cannot run a specialist."""


async def run_openai_agent(
    *,
    name: str,
    instructions: str,
    user_input: str,
    model: str,
) -> str:
    """Run a specialist agent and return its final output as text."""
    try:
        from agents import Agent, Runner
    except ImportError as exc:
        raise AgentRuntimeError("openai-agents package is not installed") from exc

    agent = Agent(name=name, instructions=instructions, model=model)
    result = await Runner.run(agent, user_input)
    final_output = getattr(result, "final_output", result)
    return str(final_output)


async def run_specialist_json(
    *,
    name: str,
    instructions: str,
    user_input: str,
    model: str,
    schema_name: str,
    settings: AppSettings,
    fallback_client: LLMClient,
) -> dict[str, Any]:
    """Run a specialist as an Agent SDK task or test-friendly fallback."""
    if settings.use_openai_agents_sdk:
        output = await run_openai_agent(
            name=name,
            instructions=instructions,
            user_input=user_input,
            model=model,
        )
        try:
            payload = json.loads(output)
        except json.JSONDecodeError as exc:
            raise InvalidLLMJSONError(
                f"{schema_name} agent output was not valid JSON: {output[:200]}"
            ) from exc
        if not isinstance(payload, dict):
            raise InvalidLLMJSONError(f"{schema_name} agent output must be a JSON object")
        return cast(dict[str, Any], payload)

    return await fallback_client.complete_json(
        model=model,
        instructions=instructions,
        user_input=user_input,
        schema_name=schema_name,
    )
