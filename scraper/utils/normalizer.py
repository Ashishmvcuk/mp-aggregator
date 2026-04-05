from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any, Optional
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

from utils.title_refine import TITLE_CAPS, refine_link_title

logger = logging.getLogger(__name__)

CATEGORY_ORDER = ("results", "news", "syllabus", "admit_cards", "blogs", "jobs")
ALLOWED_CATEGORIES = frozenset(CATEGORY_ORDER)

# Category-specific title rules (after whitespace normalize)
_MIN_TITLE_LEN: dict[str, int] = {
    "blogs": 12,
}
_DEFAULT_MIN_TITLE_LEN = 1
_MAX_TITLE_LEN = 500


def normalize_title(title: Any) -> str:
    if title is None:
        return ""
    s = str(title).strip()
    s = re.sub(r"\s+", " ", s)
    return s


def normalize_url(item_url: Any, base: str) -> Optional[str]:
    if item_url is None:
        return None
    raw = str(item_url).strip()
    if not raw:
        return None
    joined = urljoin(base, raw)
    parsed = urlparse(joined)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    return joined


def parse_date_iso(value: Any) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    head = s.split()[0][:10]
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", head)
    if m:
        try:
            datetime.strptime(head, "%Y-%m-%d")
            return head
        except ValueError:
            pass
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            chunk = s[:10] if len(s) >= 10 else s
            return datetime.strptime(chunk, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _title_ok_for_category(category: str, title: str) -> bool:
    min_len = _MIN_TITLE_LEN.get(category, _DEFAULT_MIN_TITLE_LEN)
    if len(title) < min_len:
        return False
    if len(title) > _MAX_TITLE_LEN:
        return False
    return True


def normalize_item_for_category(
    item: dict[str, Any],
    source_url: str,
    category: str,
) -> Optional[dict[str, Any]]:
    """
    Normalize a raw parser item into a canonical record.
    `category` is the merge bucket and is the source of truth for the output field.
    """
    if category not in ALLOWED_CATEGORIES:
        logger.debug("Dropped item: unknown bucket %r", category)
        return None

    declared = item.get("category")
    if declared is not None and declared != category:
        logger.debug(
            "Category mismatch: bucket=%r item.category=%r title=%r — using bucket",
            category,
            declared,
            item.get("title"),
        )

    title = normalize_title(item.get("title"))
    if not title:
        logger.debug("Dropped item: empty title (bucket=%s)", category)
        return None

    raw_url_for_title = str(item.get("url") or "").strip()
    refined = refine_link_title(title, category, raw_url_for_title)
    min_len = _MIN_TITLE_LEN.get(category, _DEFAULT_MIN_TITLE_LEN)
    if len(refined) >= min_len:
        title = refined
    elif len(title) > TITLE_CAPS.get(category, 130) + 25:
        soft = TITLE_CAPS.get(category, 130) + 40
        chunk = title[:soft]
        sp = chunk.rfind(" ")
        title = (chunk[:sp] if sp >= min_len else chunk).rstrip(",;:") + ("…" if len(title) > soft else "")
    else:
        title = refined or title

    if not _title_ok_for_category(category, title):
        logger.debug("Dropped item: title length out of range for %s (title=%r)", category, title[:80])
        return None

    uni = normalize_title(item.get("university"))
    if not uni:
        logger.debug("Dropped item: empty university (title=%r)", title)
        return None

    url = normalize_url(item.get("url"), source_url)
    if not url:
        logger.debug("Dropped item: bad url (title=%r)", title)
        return None

    date_iso = parse_date_iso(item.get("date"))
    if not date_iso:
        logger.debug("Dropped item: unparseable date (title=%r)", title)
        return None

    return {
        "university": uni,
        "title": title,
        "url": url,
        "date": date_iso,
        "category": category,
    }


def strip_tracking_query_params(url: str) -> str:
    """Remove common tracking query params; keep path and other params."""
    parsed = urlparse(url)
    if not parsed.query:
        return url
    drop_prefixes = ("utm_",)
    drop_exact = {"fbclid", "gclid", "mc_eid"}
    pairs = [
        (k, v)
        for k, v in parse_qsl(parsed.query, keep_blank_values=True)
        if k.lower() not in drop_exact and not any(k.lower().startswith(p) for p in drop_prefixes)
    ]
    new_query = urlencode(pairs)
    return urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment)
    )
