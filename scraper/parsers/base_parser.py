from __future__ import annotations

from abc import ABC, abstractmethod
import re
from datetime import date
from typing import Any, Iterator
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from utils.normalizer import CATEGORY_ORDER, find_first_iso_date_in_string, parse_dd_mon_cell


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


def iter_anchor_candidates_with_tags(
    soup: BeautifulSoup,
    source_url: str,
    *,
    min_text_len: int = 4,
) -> Iterator[tuple[str, str, Any]]:
    """Yield (absolute_url, link_text, anchor_tag) for anchors suitable for downstream normalization."""
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
        yield urljoin(source_url, href), text, a


def iter_anchor_candidates(
    soup: BeautifulSoup,
    source_url: str,
    *,
    min_text_len: int = 4,
) -> Iterator[tuple[str, str]]:
    """Yield (absolute_url, link_text) for anchors suitable for downstream normalization."""
    for abs_url, text, _ in iter_anchor_candidates_with_tags(soup, source_url, min_text_len=min_text_len):
        yield abs_url, text


def _dates_from_table_row(row: Tag) -> str | None:
    """ddMon / DD/MM/YYYY / ISO fragments in same <tr> as a link."""
    ctx = row.get_text(" ", strip=True)
    for td in row.find_all("td"):
        cell = " ".join(td.get_text().split())
        compact = re.sub(r"\s+", "", cell)
        iso = parse_dd_mon_cell(compact, ctx)
        if iso:
            return iso
        for token in re.split(r"[\s|/]+", cell):
            t = re.sub(r"\s+", "", token)
            if len(t) < 5:
                continue
            iso = parse_dd_mon_cell(t, ctx)
            if iso:
                return iso
        iso = find_first_iso_date_in_string(cell, ctx)
        if iso:
            return iso
    return None


def extract_date_near_anchor(anchor: Tag) -> str | None:
    """
    Best-effort real calendar date for results / news / jobs / admission links:
    table row first, then list item, then nearby parent text.
    """
    row = anchor.find_parent("tr")
    if row:
        d = _dates_from_table_row(row)
        if d:
            return d
    li = anchor.find_parent("li")
    if li:
        ctx = li.get_text(" ", strip=True)
        d = find_first_iso_date_in_string(ctx, ctx)
        if d:
            return d
        for word in re.split(r"[\s|]+", ctx):
            w = re.sub(r"\s+", "", word)
            if len(w) < 5:
                continue
            d = parse_dd_mon_cell(w, ctx)
            if d:
                return d
    el: Any = anchor
    for _ in range(5):
        if el is None or not hasattr(el, "get_text"):
            break
        txt = el.get_text(" ", strip=True)
        if len(txt) > 800:
            txt = txt[:800]
        d = find_first_iso_date_in_string(txt, txt)
        if d:
            return d
        el = getattr(el, "parent", None)
    return None


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
