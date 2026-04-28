"""Prompt and knowledge-packet loading utilities."""

from __future__ import annotations

from pathlib import Path


class PromptNotFoundError(FileNotFoundError):
    """Raised when a prompt packet is missing."""


def load_prompt(name: str, root: Path | None = None) -> str:
    """Load a prompt markdown file from the prompts directory.

    Args:
        name: Prompt filename with or without the `.md` suffix.
        root: Optional repository root override for tests.

    Returns:
        UTF-8 prompt contents.

    Raises:
        PromptNotFoundError: If the prompt file is missing.
    """
    repo_root = Path.cwd() if root is None else root
    filename = name if name.endswith(".md") else f"{name}.md"
    path = repo_root / "prompts" / filename
    if not path.exists():
        raise PromptNotFoundError(path)
    return path.read_text(encoding="utf-8")
