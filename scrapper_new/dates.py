"""Self-contained date parsing (subset of ideas from scraper/utils/normalizer.py)."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any, Optional

_MONTH_ABBREV = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

_DATE_FRAGMENT = re.compile(
    r"\b(\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|"
    r"\d{4}[./-]\d{1,2}[./-]\d{1,2}|"
    r"\d{1,2}-[A-Za-z]{3}-\d{4})\b"
)


def parse_date_iso(value: Any) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    first_tok = s.split()[0]
    if re.match(r"^\d{1,2}-[A-Za-z]{3}-\d{4}$", first_tok, re.I):
        try:
            return datetime.strptime(first_tok, "%d-%b-%Y").date().isoformat()
        except ValueError:
            pass
    head = s.split()[0][:10]
    if re.match(r"^(\d{4})-(\d{2})-(\d{2})$", head):
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


def find_first_iso_date_in_string(text: str, _context: str = "") -> Optional[str]:
    if not text or not str(text).strip():
        return None
    t = str(text).strip()
    iso = parse_date_iso(t)
    if iso:
        return iso
    for m in _DATE_FRAGMENT.finditer(t):
        iso = parse_date_iso(m.group(1))
        if iso:
            return iso
    return None


def parse_http_date_header(value: str | None) -> Optional[date]:
    """RFC 7231 IMF-fixdate subset via email.utils."""
    if not value or not str(value).strip():
        return None
    try:
        from email.utils import parsedate_to_datetime

        dt = parsedate_to_datetime(value.strip())
        if dt is None:
            return None
        return dt.date()
    except (TypeError, ValueError, OverflowError):
        return None


def parse_iso_datetime_attr(value: str | None) -> Optional[str]:
    """HTML time datetime= often YYYY-MM-DD or full ISO."""
    if not value or not str(value).strip():
        return None
    s = str(value).strip()
    head = s[:10]
    if re.match(r"^\d{4}-\d{2}-\d{2}$", head):
        try:
            date.fromisoformat(head)
            return head
        except ValueError:
            return None
    iso = parse_date_iso(s)
    return iso
