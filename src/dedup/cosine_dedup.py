"""Simple token cosine deduplication for extracted issues."""

from __future__ import annotations

import math
from collections import Counter

from src.config import ISSUE_DEDUP_THRESHOLD
from src.schemas import Issue


def deduplicate_issues(
    issues: tuple[Issue, ...],
    *,
    threshold: float = ISSUE_DEDUP_THRESHOLD,
) -> tuple[Issue, ...]:
    """Merge near-duplicate issues using token cosine similarity."""
    kept: list[Issue] = []
    for issue in issues:
        if not any(_cosine(issue, existing) >= threshold for existing in kept):
            kept.append(issue)
    return tuple(kept)


def _cosine(left: Issue, right: Issue) -> float:
    left_counts = _token_counts(left)
    right_counts = _token_counts(right)
    if not left_counts or not right_counts:
        return 0.0
    shared = set(left_counts) & set(right_counts)
    numerator = sum(left_counts[token] * right_counts[token] for token in shared)
    left_norm = math.sqrt(sum(count * count for count in left_counts.values()))
    right_norm = math.sqrt(sum(count * count for count in right_counts.values()))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return numerator / (left_norm * right_norm)


def _token_counts(issue: Issue) -> Counter[str]:
    text = " ".join((issue.title, issue.description, " ".join(issue.keywords)))
    tokens = (token.strip().lower() for token in text.split())
    return Counter(token for token in tokens if token)
