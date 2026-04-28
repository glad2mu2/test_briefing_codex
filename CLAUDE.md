# CLAUDE.md

This file is legacy context from the original Claude Code-oriented design.

The active coding-agent guidance is now `AGENTS.md`, and the active runtime design is `DESIGN.md`.

Do not add new Claude Code, Claude Agent SDK, Anthropic model, or `.claude/skills` requirements here unless provider support is explicitly reopened.

Migration decision, 2026-04-28:

- Development agent: Codex.
- Runtime LLM provider: OpenAI API.
- Runtime orchestration: Python Layer 0 orchestrator plus OpenAI Agents SDK / Responses API.
- Knowledge packets: `prompts/`, not `.claude/skills/`.
- API key: `OPENAI_API_KEY`, not `ANTHROPIC_API_KEY`.
