"""Shorten and focus link titles scraped from university portals (UI tables)."""
from __future__ import annotations

import re
from pathlib import PurePath
from urllib.parse import unquote, urlparse

# Max visible length per category after refinement (exported for normalizer fallbacks)
TITLE_CAPS: dict[str, int] = {
    "results": 118,
    "news": 140,
    "syllabus": 110,
    "admit_cards": 110,
    "blogs": 165,
    "jobs": 115,
}
_DEFAULT_CAP = 130

_NOISE_PREFIX = re.compile(
    r"^\s*(click\s+here\s*(to|for)?\s*|read\s+more\s*|more\s*[.\u2026…]*\s*|"
    r"apply\s+here\s*|tap\s+here\s*|tap\s+to\s*|"
    r"home\s*[>|]\s*|welcome\s*[>|]\s*)",
    re.I,
)


def _humanize_filename_stem(url: str, max_len: int) -> str:
    path = unquote(urlparse(url).path or "")
    stem = PurePath(path).stem
    if not stem or stem.lower() in ("index", "default", "page", "view", "form"):
        return ""
    s = re.sub(r"[_\-.]+", " ", stem)
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) < 4:
        return ""
    return s[:max_len]


def refine_link_title(title: str, category: str, url: str = "") -> str:
    """
    Produce a shorter, headline-style title for dashboard columns.
    Safe to call after whitespace normalization.
    """
    if not title:
        return title
    t = re.sub(r"\s+", " ", str(title).strip())
    if not t:
        return t

    t = _NOISE_PREFIX.sub("", t).strip()
    if not t:
        return str(title).strip()[: _DEFAULT_CAP]

    # First segment before a separator is usually the real headline
    for sep in (" | ", " – ", " — ", " :: ", " // ", "\n"):
        if sep in t:
            head, tail = t.split(sep, 1)
            head = head.strip()
            if len(head) >= 12:
                t = head
                break

    cap = TITLE_CAPS.get(category, _DEFAULT_CAP)

    # For results, prefer a clause mentioning exam/result if the line is huge
    if category == "results" and len(t) > cap + 15:
        m = re.search(
            r"([^.!?\n]{0,25}(?:result|exam|marksheet|mark\s*sheet|score\s*card|revaluation|semester|main\s+exam)[^.!?\n]{0,80})",
            t,
            re.I,
        )
        if m:
            snippet = re.sub(r"\s+", " ", m.group(1).strip())
            if len(snippet) >= 14:
                t = snippet

    if len(t) > cap:
        chunk = t[:cap]
        end = -1
        for p in ".?!":
            i = chunk.rfind(p)
            if i >= max(36, cap // 3):
                end = max(end, i)
        if end >= 0:
            t = t[: end + 1].strip()
        else:
            sp = chunk.rfind(" ")
            if sp >= cap * 0.5:
                t = chunk[:sp].rstrip(",;:") + "…"
            else:
                t = chunk.rstrip(",;:") + "…"

    # If we stripped too aggressively, enrich from URL path (e.g. Result2024.aspx)
    if len(t) < 10 and url:
        hint = _humanize_filename_stem(url, 48)
        if hint:
            t = f"{t} ({hint})".strip() if t else hint
            t = t[: cap + 25]

    return t[:500]
