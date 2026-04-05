from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Iterator
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from utils.normalizer import CATEGORY_ORDER


def default_today_iso() -> str:
    return date.today().isoformat()


def empty_categories() -> dict[str, list[dict[str, Any]]]:
    return {c: [] for c in CATEGORY_ORDER}


def raw_item(
    university: str,
    title: str,
    url: str,
    category: str,
    date: str | None = None,
) -> dict[str, Any]:
    return {
        "university": university,
        "title": title,
        "url": url,
        "date": date if date is not None else default_today_iso(),
        "category": category,
    }


def iter_anchor_candidates(
    soup: BeautifulSoup,
    source_url: str,
    *,
    min_text_len: int = 4,
) -> Iterator[tuple[str, str]]:
    """Yield (absolute_url, link_text) for anchors suitable for downstream normalization."""
    for a in soup.find_all("a", href=True):
        href = (a.get("href") or "").strip()
        visible = " ".join(a.get_text().split())
        title_attr = " ".join((a.get("title") or "").split())
        text = visible
        # Long visible text is often a whole table row; <a title="…"> is usually the real label
        if title_attr and len(title_attr) >= 8 and len(visible) > 72:
            if len(title_attr) <= min(len(visible) - 1, 220):
                text = title_attr
        elif title_attr and len(visible) > 160 and 8 <= len(title_attr) <= 180:
            text = title_attr
        if not href or not text or len(text) < min_text_len:
            continue
        low = href.lower()
        if low.startswith(("javascript:", "mailto:", "#")):
            continue
        yield urljoin(source_url, href), text


def ensure_category_keys(d: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Ensure every category key exists (defensive after parse())."""
    out = empty_categories()
    for k in CATEGORY_ORDER:
        v = d.get(k)
        if v:
            out[k] = list(v)
    return out


class BaseParser(ABC):
    """Parse HTML into category buckets (empty lists allowed)."""

    @abstractmethod
    def parse(self, html: str, university: str, source_url: str) -> dict[str, list[dict[str, Any]]]:
        """Return keys for all allowed categories; each item is a loose dict pre-normalization."""
