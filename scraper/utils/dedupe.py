from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

from utils.normalizer import strip_tracking_query_params

logger = logging.getLogger(__name__)

# results/syllabus/admit_cards: same URL (after stripping tracking params) => duplicate.
# news/blogs: URL often unstable — dedupe by (title_lower, netloc).
_URL_KEY_CATEGORIES = frozenset({"results", "syllabus", "admit_cards"})
_TITLE_NETLOC_CATEGORIES = frozenset({"news", "blogs", "jobs"})


def _dedupe_key(category: str, item: dict[str, Any]) -> str:
    url = (item.get("url") or "").strip()
    title = (item.get("title") or "").strip().lower()
    if category in _URL_KEY_CATEGORIES:
        cleaned = strip_tracking_query_params(url).lower()
        return f"u:{cleaned}"
    if category in _TITLE_NETLOC_CATEGORIES:
        netloc = urlparse(url).netloc.lower()
        return f"t:{title}\nhost:{netloc}"
    # default: URL key
    cleaned = strip_tracking_query_params(url).lower()
    return f"u:{cleaned}"


def dedupe_category(category: str, items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """First wins; returns (unique_list, removed_count)."""
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    removed = 0
    for it in items:
        k = _dedupe_key(category, it)
        if k in seen:
            removed += 1
            logger.debug("Dedupe skip [%s]: %s", category, k[:120])
            continue
        seen.add(k)
        out.append(it)
    return out, removed
