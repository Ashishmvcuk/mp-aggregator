"""Heuristic portal parser for MP university homepages — classifies links into all categories."""
from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from parsers.base_parser import (
    BaseParser,
    empty_categories,
    extract_date_near_anchor,
    iter_anchor_candidates_with_tags,
    raw_item,
)

# First matching rule wins (order matters: specific before broad).
_CLASSIFICATION_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "admit_cards",
        (
            "admit card",
            "admit-card",
            "hall ticket",
            "e-admit",
            "eadmit",
            "call letter",
            "download admit",
            "entrance admit",
        ),
    ),
    (
        "enrollments",
        (
            "enrollment",
            "enrolment",
            "enrol",
            "admission",
            "admissions",
            "intake",
            "prospectus",
            "counselling",
            "counseling",
            "spot admission",
            "spot counselling",
            "spot counseling",
            "application form",
            "seat allotment",
            "counselling round",
            "counseling round",
            "mphil admission",
            "ph.d admission",
            "phd admission",
        ),
    ),
    (
        "jobs",
        (
            "recruitment",
            "vacancy",
            "vacancies",
            "faculty position",
            "faculty recruitment",
            "walk-in",
            "walk in",
            "walkin",
            "career",
            "naukri",
            "job opening",
            "jobs at",
            "engagement of",
            "contractual engagement",
            "guest faculty",
        ),
    ),
    (
        "results",
        (
            "result",
            "marksheet",
            "mark sheet",
            "scorecard",
            "score card",
            "revaluation",
            "exam result",
            "semester result",
            "main exam",
            "back paper",
            "time table",
            "time-table",
            "timetable",
            "exam schedule",
            "date sheet",
        ),
    ),
    (
        "syllabus",
        (
            "syllabus",
            "curriculum",
            "scheme of examination",
            "scheme of exam",
            "regulation",
            "course structure",
        ),
    ),
    (
        "news",
        (
            "news",
            "notice",
            "circular",
            "announcement",
            "notification",
            "tender",
            "press release",
            "press note",
            "latest news",
            "university news",
        ),
    ),
    (
        "blogs",
        (
            "blog",
            "editorial",
            "article",
            "magazine",
        ),
    ),
)

_MAX_PER_CATEGORY = 40


def _norm_url_dedupe(url: str) -> str:
    return url.strip().rstrip("/")


def _page_title(soup: BeautifulSoup) -> str:
    tag = soup.find("title")
    if tag:
        t = tag.get_text(" ", strip=True)
        if t:
            return t[:500]
    for h in soup.find_all(["h1", "h2"], limit=3):
        t = h.get_text(" ", strip=True)
        if t and len(t) >= 4:
            return t[:500]
    return ""


def _infer_seed_page_category(url: str) -> str | None:
    """
    When fetching extra portal URLs (seed_urls), classify the page itself if anchors are sparse.
    Order: specific paths before generic /login.
    """
    u = url.lower()
    p = urlparse(url)
    path = (p.path or "").lower()
    q = (p.query or "").lower()
    blob = f"{u} {path} {q}"
    if any(x in blob for x in ("admit", "hall-ticket", "hallticket", "e-admit", "call-letter")):
        return "admit_cards"
    if any(
        x in blob
        for x in (
            "syllabus",
            "scheme",
            "curriculum",
            "course-structure",
            "search-course-syllabus",
        )
    ):
        return "syllabus"
    compact = blob.replace(" ", "").replace("_", "")
    # Exam listings / notifications (before generic "announcement" → news)
    if "publicexamnotification" in compact or "/publicexam" in path:
        return "results"
    if "examinationannouncement" in compact:
        return "news"
    if any(
        x in blob
        for x in (
            "time-table",
            "timetable",
            "time_table",
            "exam-time",
            "exam/result",
            "result",
            "marksheet",
            "viewall",
            "exam-notification",
        )
    ) or ("examination" in blob and "announcement" not in blob):
        return "results"
    if any(
        x in blob
        for x in (
            "announcement",
            "notification",
            "news",
            "notice",
            "newsletter",
            "news-events",
            "latest-notice",
        )
    ):
        return "news"
    if any(
        x in blob
        for x in (
            "studentlogin",
            "student_login",
            "student_panel",
            "erp-login",
            "/login",
            "accsoft",
        )
    ):
        return "enrollments"
    return None


def _classify_link(text: str, abs_url: str) -> str | None:
    path = (urlparse(abs_url).path or "").lower()
    blob = f"{text} {path} {abs_url.lower()}".lower()
    for category, keywords in _CLASSIFICATION_RULES:
        for kw in keywords:
            if kw in blob:
                return category
    return None


def _skip_enrollment_utility_url(abs_url: str) -> bool:
    """Drop bus / IQAC feedback / misc fee portals — not admission notices."""
    u = abs_url.lower().replace("\\", "/")
    if "busportal" in u or "buspayment" in u or "/bus/" in u:
        return True
    if "feedback" in u and ("home" in u or "feed" in u):
        return True
    if "onlinefee" in u and "misc" in u:
        return True
    if "onlinefeeform" in u and "misc" in u:
        return True
    return False


class MpPortalParser(BaseParser):
    """Extract anchor links from a university portal using keyword buckets."""

    def parse(self, html: str, university: str, source_url: str) -> dict[str, list[dict[str, Any]]]:
        out = empty_categories()
        per_cat: dict[str, int] = {c: 0 for c in out}
        seen_url: set[str] = set()

        soup = BeautifulSoup(html, "html.parser")
        for abs_url, text, anchor in iter_anchor_candidates_with_tags(soup, source_url, min_text_len=3):
            key = _norm_url_dedupe(abs_url)
            if key in seen_url:
                continue
            category = _classify_link(text, abs_url)
            if category is None:
                continue
            if category == "enrollments" and _skip_enrollment_utility_url(abs_url):
                continue
            if per_cat[category] >= _MAX_PER_CATEGORY:
                continue
            seen_url.add(key)
            row_date = extract_date_near_anchor(anchor)
            out[category].append(
                raw_item(university, text[:500], abs_url, category, date=row_date),
            )
            per_cat[category] += 1

        # Seed URLs (time table, results, etc.): add the fetched page as an item when the URL
        # clearly maps to a category and the page was not already emitted as a link target.
        src_key = _norm_url_dedupe(source_url)
        if src_key not in seen_url:
            inferred = _infer_seed_page_category(source_url)
            if inferred == "enrollments" and _skip_enrollment_utility_url(source_url):
                inferred = None
            if inferred is not None and per_cat[inferred] < _MAX_PER_CATEGORY:
                title = _page_title(soup) or source_url
                seen_url.add(src_key)
                out[inferred].append(
                    raw_item(university, title[:500], source_url, inferred, date=None),
                )
                per_cat[inferred] += 1

        return out
