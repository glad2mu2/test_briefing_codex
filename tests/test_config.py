"""Tests for environment-backed settings."""

from __future__ import annotations

from src.config import load_settings


def test_load_settings_defaults_are_openai_quality_first() -> None:
    settings = load_settings({})
    assert settings.openai_api_key is None
    assert settings.use_openai_agents_sdk is True
    assert settings.allow_openai_text_upload is False
    assert settings.models.issue_extraction == "gpt-5.5"
    assert settings.models.classification == "gpt-5.4-mini"


def test_load_settings_env_overrides() -> None:
    settings = load_settings(
        {
            "OPENAI_API_KEY": "sk-test",
            "USE_OPENAI_AGENTS_SDK": "false",
            "ALLOW_OPENAI_TEXT_UPLOAD": "true",
            "OPENAI_ISSUE_MODEL": "custom-issue",
            "OUTPUT_DIR": "custom-output",
            "STATE_DIR": "custom-state",
        }
    )
    assert settings.openai_api_key == "sk-test"
    assert settings.use_openai_agents_sdk is False
    assert settings.allow_openai_text_upload is True
    assert settings.models.issue_extraction == "custom-issue"
    assert settings.output_dir.as_posix() == "custom-output"
    assert settings.state_dir.as_posix() == "custom-state"
