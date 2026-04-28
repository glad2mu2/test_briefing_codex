"""Deterministic media extraction from article HTML."""

from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class ArticleMedia:
    """Media candidates extracted from article HTML."""

    image_url: str | None
    table_count: int


def extract_article_media(html: str, *, base_url: str | None = None) -> ArticleMedia:
    """Extract the best image URL and table count from article HTML."""
    soup = BeautifulSoup(html, "html.parser")
    image_url = _meta_content(soup, "og:image") or _first_image_src(soup)
    if image_url and base_url and image_url.startswith("/"):
        image_url = base_url.rstrip("/") + image_url
    return ArticleMedia(image_url=image_url, table_count=len(soup.find_all("table")))


def _meta_content(soup: BeautifulSoup, property_name: str) -> str | None:
    meta = soup.find("meta", property=property_name)
    if meta is None:
        return None
    content = meta.get("content")
    return content if isinstance(content, str) and content else None


def _first_image_src(soup: BeautifulSoup) -> str | None:
    image = soup.find("img")
    if image is None:
        return None
    src = image.get("src")
    return src if isinstance(src, str) and src else None
