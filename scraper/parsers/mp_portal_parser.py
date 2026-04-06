"""Heuristic portal parser for MP university homepages — classifies links into all categories."""
from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from parsers.base_parser import BaseParser, empty_categories, iter_anchor_candidates, raw_item

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


def _classify_link(text: str, abs_url: str) -> str | None:
    path = (urlparse(abs_url).path or "").lower()
    blob = f"{text} {path} {abs_url.lower()}".lower()
    for category, keywords in _CLASSIFICATION_RULES:
        for kw in keywords:
            if kw in blob:
                return category
    return None


class MpPortalParser(BaseParser):
    """Extract anchor links from a university portal using keyword buckets."""

    def parse(self, html: str, university: str, source_url: str) -> dict[str, list[dict[str, Any]]]:
        out = empty_categories()
        per_cat: dict[str, int] = {c: 0 for c in out}
        seen_url: set[str] = set()

        soup = BeautifulSoup(html, "html.parser")
        for abs_url, text in iter_anchor_candidates(soup, source_url, min_text_len=3):
            if abs_url in seen_url:
                continue
            category = _classify_link(text, abs_url)
            if category is None:
                continue
            if per_cat[category] >= _MAX_PER_CATEGORY:
                continue
            seen_url.add(abs_url)
            out[category].append(
                raw_item(university, text[:500], abs_url, category),
            )
            per_cat[category] += 1

        return out
