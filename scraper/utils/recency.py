"""
Rolling-window filter on normalized scraped rows (live `main.py` only).

After each link is parsed and normalized into a record (all categories: results,
news, syllabus, etc.), we keep the row only if its announcement `date` parses as
YYYY-MM-DD and is >= cutoff. Fetch URLs are always requested; filtering applies
only to extracted dataset rows, not to whether a portal was scraped.
"""
from __future__ import annotations

import os
import re
from datetime import date, datetime, timedelta, timezone
from typing import Any

_DEFAULT_RECENCY_DAYS = 60


def recency_days_from_env() -> int | None:
    """
    Days to look back from run date (UTC calendar date).
    Returns None when SCRAPER_RECENCY_DAYS is 0 or negative (filter disabled).
    Default when unset: 60 days.
    """
    raw = os.environ.get("SCRAPER_RECENCY_DAYS", str(_DEFAULT_RECENCY_DAYS)).strip()
    try:
        n = int(raw)
    except ValueError:
        n = _DEFAULT_RECENCY_DAYS
    if n <= 0:
        return None
    return n


def cutoff_date_for_run(reference_utc: datetime, days: int) -> date:
    """Inclusive lower bound: items with date >= this day are kept."""
    return reference_utc.astimezone(timezone.utc).date() - timedelta(days=days)


def parse_item_announcement_date(item: dict[str, Any]) -> date | None:
    """Parse normalized item `date` as YYYY-MM-DD; invalid or missing → None."""
    d = item.get("date")
    if not d or not isinstance(d, str):
        return None
    head = d.strip().split()[0][:10]
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", head):
        return None
    try:
        return date.fromisoformat(head)
    except ValueError:
        return None


def keep_item_for_recency(item: dict[str, Any], cutoff: date) -> bool:
    """Strict: require a parseable date on or after cutoff."""
    parsed = parse_item_announcement_date(item)
    if parsed is None:
        return False
    return parsed >= cutoff


def item_json_log_enabled() -> bool:
    return os.environ.get("SCRAPER_ITEM_LOG", "").strip().lower() in ("1", "true", "yes")
