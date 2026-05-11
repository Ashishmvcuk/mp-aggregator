"""HTML → candidate update rows (anchors + context)."""

from __future__ import annotations

import logging
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from scrapper_new.categories import refine_content_kind
from scrapper_new.dates import find_first_iso_date_in_string, parse_iso_datetime_attr
from scrapper_new.models import RawExtracted

logger = logging.getLogger(__name__)

_MAX_DESC = 280
_MIN_TITLE = 4
_SKIP_TITLE_RE = re.compile(
    r"^(home|click here|read more|more|next|previous|login|sign in|menu)\b",
    re.I,
)


def _ancestor_context(tag: Tag, max_depth: int = 4) -> str:
    parts: list[str] = []
    cur: Tag | None = tag
    depth = 0
    while cur is not None and depth < max_depth:
        if cur.name in ("tr", "li", "article", "div", "td"):
            t = cur.get_text(" ", strip=True)
            if len(t) > 20:
                parts.append(t[:400])
        cur = cur.parent  # type: ignore[assignment]
        depth += 1
        if isinstance(cur, Tag) and cur.name == "body":
            break
    return " ".join(parts)


def _time_tags_near(tag: Tag) -> str | None:
    cur: Tag | None = tag
    for _ in range(6):
        if cur is None:
            break
        for tsel in cur.find_all("time", limit=5):
            dt = parse_iso_datetime_attr(tsel.get("datetime"))
            if dt:
                return dt
        cur = cur.parent  # type: ignore[assignment]
    return None


def extract_from_html(
    html: str,
    *,
    source_page_url: str,
    university: str,
    content_kind_hint: str,
) -> list[RawExtracted]:
    if not html or not html.strip():
        return []
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception as e:  # noqa: BLE001 — bad HTML
        logger.warning("parse_html_failed url=%s err=%s", source_page_url, e)
        return []

    out: list[RawExtracted] = []
    for a in soup.find_all("a", href=True):
        href = (a.get("href") or "").strip()
        if not href or href.startswith(("#", "javascript:", "mailto:")):
            continue
        visible = " ".join(a.get_text().split())
        title_attr = " ".join((a.get("title") or "").split())
        text = visible
        if title_attr and len(title_attr) >= 8 and len(visible) > 72:
            if len(title_attr) <= min(len(visible) - 1, 220):
                text = title_attr
        elif title_attr and len(visible) > 160 and 8 <= len(title_attr) <= 180:
            text = title_attr
        if len(text) < _MIN_TITLE:
            continue
        if _SKIP_TITLE_RE.match(text.strip()):
            continue

        abs_url = urljoin(source_page_url, href)
        p = urlparse(abs_url)
        if p.scheme not in ("http", "https") or not p.netloc:
            continue

        ctx = _ancestor_context(a)
        blob = f"{text} {title_attr} {ctx}"
        published = find_first_iso_date_in_string(blob, blob)
        raw_cell: str | None = None
        if not published:
            published = _time_tags_near(a)
        if not published:
            # single-line context often has dd/mm/yyyy
            published = find_first_iso_date_in_string(ctx[:500], ctx)

        desc = (ctx or text)[:_MAX_DESC]
        kind = refine_content_kind(content_kind_hint, text, abs_url)

        out.append(
            RawExtracted(
                university=university,
                title=text.strip(),
                url=abs_url,
                source_page_url=source_page_url,
                description=desc,
                content_kind=kind,
                published_date_iso=published,
                published_date_raw=published,
            )
        )

    # De-dupe anchors same URL on one page (keep longest title)
    by_url: dict[str, RawExtracted] = {}
    for item in out:
        prev = by_url.get(item.url)
        if prev is None or len(item.title) > len(prev.title):
            by_url[item.url] = item
    return list(by_url.values())
