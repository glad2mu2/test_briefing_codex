"""Project-wide constants and environment-backed settings.

Source of truth: AGENTS.md and DESIGN.md.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final

# Trusted source whitelist for news search. See AGENTS.md.
SOURCE_WHITELIST_TIER_1: Final[tuple[dict[str, str], ...]] = (
    {"name": "KFCC", "url": "https://www.kfcc.or.kr"},
    {"name": "CERIK", "url": "https://www.cerik.re.kr"},
    {"name": "MOLIT", "url": "https://www.molit.go.kr"},
    {"name": "CAK", "url": "https://www.cak.or.kr"},
)

SOURCE_WHITELIST_TIER_2: Final[tuple[dict[str, str], ...]] = (
    {"name": "건설경제신문", "url": "https://www.cnews.co.kr"},
    {"name": "매일건설신문", "url": "https://www.mcnews.co.kr"},
    {"name": "대한경제", "url": "https://www.dnews.co.kr"},
)

SOURCE_WHITELIST_TIER_3: Final[tuple[str, ...]] = (
    "한국경제",
    "매일경제",
    "서울경제",
    "조선비즈",
)

# Domestic news collection priority for related articles.
# Codex-assisted runs and api_auto news research must follow this order.
DOMESTIC_NEWS_SOURCE_PRIORITY: Final[tuple[dict[str, str], ...]] = (
    {
        "tier": "1",
        "name": "대한경제",
        "url": "https://www.dnews.co.kr/",
        "type": "site",
    },
    {
        "tier": "2",
        "name": "한국경제 부동산 RSS",
        "url": "https://www.hankyung.com/feed/realestate",
        "type": "rss",
    },
    {
        "tier": "2",
        "name": "한국경제 경제 RSS",
        "url": "https://www.hankyung.com/feed/economy",
        "type": "rss",
    },
    {
        "tier": "3",
        "name": "서울경제 부동산 RSS",
        "url": "https://www.sedaily.com/rss/realestate",
        "type": "rss",
    },
    {
        "tier": "3",
        "name": "서울경제 경제 RSS",
        "url": "https://www.sedaily.com/rss/economy",
        "type": "rss",
    },
    {
        "tier": "4",
        "name": "연합뉴스 최신기사 RSS",
        "url": "https://www.yna.co.kr/rss/news.xml",
        "type": "fallback_rss",
    },
    {
        "tier": "4",
        "name": "국토일보 RSS",
        "url": "http://www.ikld.kr/rss/allArticle.xml",
        "type": "fallback_rss",
    },
    {
        "tier": "4",
        "name": "네이버 뉴스",
        "url": "https://news.naver.com/",
        "type": "fallback_site",
    },
)

DOMESTIC_NEWS_DOMAINS: Final[tuple[str, ...]] = (
    "dnews.co.kr",
    "hankyung.com",
    "sedaily.com",
    "yna.co.kr",
    "ikld.kr",
    "news.naver.com",
)

# Issue classification categories. See AGENTS.md.
ISSUE_CATEGORIES: Final[tuple[str, ...]] = (
    "cost",
    "orders",
    "safety",
    "tech",
    "labor",
    "regulation",
    "market",
)

# UTF-8 byte count including spaces. See AGENTS.md.
SUMMARY_MIN_BYTES: Final[int] = 1000
SUMMARY_MAX_BYTES: Final[int] = 2000

# Backward-compatible alias for older imports. New code should use byte limits.
SUMMARY_MAX_CHARS: Final[int] = SUMMARY_MAX_BYTES

# Cache cleanup threshold. See AGENTS.md.
CACHE_RETENTION_DAYS: Final[int] = 30

# Upload validation. Mirrors DESIGN.md §4 step [1].
MAX_UPLOAD_PDF_SIZE_MB: Final[int] = 50

# Cosine-similarity threshold for issue dedup. See DESIGN.md §4 step [3].
ISSUE_DEDUP_THRESHOLD: Final[float] = 0.85

# Polite scraping interval (seconds). See AGENTS.md.
SCRAPE_REQUEST_INTERVAL_SEC: Final[float] = 1.0

# OpenAI runtime defaults. Quality-first routing; all values are env-overridable.
DEFAULT_ISSUE_MODEL: Final[str] = "gpt-5.5"
DEFAULT_NEWS_MODEL: Final[str] = "gpt-5.4"
DEFAULT_SUMMARY_MODEL: Final[str] = "gpt-5.4-mini"
DEFAULT_FACT_CHECK_MODEL: Final[str] = "gpt-5.5"
DEFAULT_CLASSIFIER_MODEL: Final[str] = "gpt-5.4-mini"
DEFAULT_LAYOUT_MODEL: Final[str] = "gpt-5.5"

DEFAULT_OUTPUT_DIR: Final[Path] = Path("data/output")
DEFAULT_STATE_DIR: Final[Path] = Path("data/extracted")

OPENAI_PROVIDER_NAME: Final[str] = "openai"

CODEX_ASSISTED_MODE: Final[str] = "codex_assisted"
API_AUTO_MODE: Final[str] = "api_auto"


def format_domestic_news_source_priority() -> str:
    """Return the domestic news source priority as a prompt-ready string."""
    return "\n".join(
        f"{source['tier']}. {source['name']} ({source['type']}): {source['url']}"
        for source in DOMESTIC_NEWS_SOURCE_PRIORITY
    )


@dataclass(frozen=True)
class ModelRouting:
    """Model names used by each AI stage."""

    issue_extraction: str = DEFAULT_ISSUE_MODEL
    news_research: str = DEFAULT_NEWS_MODEL
    summarization: str = DEFAULT_SUMMARY_MODEL
    fact_check: str = DEFAULT_FACT_CHECK_MODEL
    classification: str = DEFAULT_CLASSIFIER_MODEL
    layout: str = DEFAULT_LAYOUT_MODEL


@dataclass(frozen=True)
class AppSettings:
    """Runtime settings loaded from environment variables."""

    run_mode: str
    openai_api_key: str | None
    use_openai_agents_sdk: bool
    allow_openai_text_upload: bool
    output_dir: Path
    state_dir: Path
    log_level: str
    models: ModelRouting


def load_settings(env: Mapping[str, str] | None = None) -> AppSettings:
    """Load runtime settings from a mapping, defaulting to process env.

    Args:
        env: Optional environment mapping for tests.

    Returns:
        AppSettings populated with defaults and environment overrides.
    """
    source = os.environ if env is None else env
    models = ModelRouting(
        issue_extraction=source.get("OPENAI_ISSUE_MODEL", DEFAULT_ISSUE_MODEL),
        news_research=source.get("OPENAI_NEWS_MODEL", DEFAULT_NEWS_MODEL),
        summarization=source.get("OPENAI_SUMMARY_MODEL", DEFAULT_SUMMARY_MODEL),
        fact_check=source.get("OPENAI_FACT_CHECK_MODEL", DEFAULT_FACT_CHECK_MODEL),
        classification=source.get("OPENAI_CLASSIFIER_MODEL", DEFAULT_CLASSIFIER_MODEL),
        layout=source.get("OPENAI_LAYOUT_MODEL", DEFAULT_LAYOUT_MODEL),
    )
    return AppSettings(
        run_mode=source.get("BRIEFING_RUN_MODE", CODEX_ASSISTED_MODE),
        openai_api_key=_clean_optional(source.get("OPENAI_API_KEY")),
        use_openai_agents_sdk=_env_bool(
            source.get("USE_OPENAI_AGENTS_SDK"),
            default=False,
        ),
        allow_openai_text_upload=_env_bool(
            source.get("ALLOW_OPENAI_TEXT_UPLOAD"),
            default=False,
        ),
        output_dir=Path(source.get("OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR))),
        state_dir=Path(source.get("STATE_DIR", str(DEFAULT_STATE_DIR))),
        log_level=source.get("LOG_LEVEL", "INFO"),
        models=models,
    )


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _env_bool(value: str | None, *, default: bool) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    return default
