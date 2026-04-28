"""Tests for environment-backed settings."""

from __future__ import annotations

from src.config import (
    DOMESTIC_NEWS_SOURCE_PRIORITY,
    format_domestic_news_source_priority,
    load_settings,
)


def test_load_settings_defaults_are_openai_quality_first() -> None:
    settings = load_settings({})
    assert settings.run_mode == "codex_assisted"
    assert settings.openai_api_key is None
    assert settings.use_openai_agents_sdk is False
    assert settings.allow_openai_text_upload is False
    assert settings.models.issue_extraction == "gpt-5.5"
    assert settings.models.classification == "gpt-5.4-mini"


def test_load_settings_env_overrides() -> None:
    settings = load_settings(
        {
            "OPENAI_API_KEY": "sk-test",
            "BRIEFING_RUN_MODE": "api_auto",
            "USE_OPENAI_AGENTS_SDK": "false",
            "ALLOW_OPENAI_TEXT_UPLOAD": "true",
            "OPENAI_ISSUE_MODEL": "custom-issue",
            "OUTPUT_DIR": "custom-output",
            "STATE_DIR": "custom-state",
        }
    )
    assert settings.run_mode == "api_auto"
    assert settings.openai_api_key == "sk-test"
    assert settings.use_openai_agents_sdk is False
    assert settings.allow_openai_text_upload is True
    assert settings.models.issue_extraction == "custom-issue"
    assert settings.output_dir.as_posix() == "custom-output"
    assert settings.state_dir.as_posix() == "custom-state"


def test_domestic_news_source_priority_matches_required_order() -> None:
    names = tuple(source["name"] for source in DOMESTIC_NEWS_SOURCE_PRIORITY)

    assert names == (
        "대한경제",
        "한국경제 부동산 RSS",
        "한국경제 경제 RSS",
        "서울경제 부동산 RSS",
        "서울경제 경제 RSS",
        "연합뉴스 최신기사 RSS",
        "국토일보 RSS",
        "네이버 뉴스",
    )
    assert DOMESTIC_NEWS_SOURCE_PRIORITY[0]["url"] == "https://www.dnews.co.kr/"
    assert DOMESTIC_NEWS_SOURCE_PRIORITY[-1]["url"] == "https://news.naver.com/"


def test_format_domestic_news_source_priority_includes_rss_urls() -> None:
    formatted = format_domestic_news_source_priority()

    assert "https://www.hankyung.com/feed/realestate" in formatted
    assert "https://www.sedaily.com/rss/economy" in formatted
    assert "https://www.yna.co.kr/rss/news.xml" in formatted
