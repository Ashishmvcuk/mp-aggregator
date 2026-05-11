from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

DateConfidence = Literal["high", "medium", "low"]

WEBSITE_CATEGORIES = frozenset(
    {"results", "news", "syllabus", "admit_cards", "enrollments", "blogs", "jobs"}
)


@dataclass
class UrlTask:
    """One HTTP target for a university."""

    university: str
    url: str
    source_field: str
    content_kind_hint: str


@dataclass
class FetchResult:
    url: str
    ok: bool
    status_code: int | None = None
    error: str | None = None
    html: str | None = None
    content_type: str | None = None
    last_modified: str | None = None  # raw header value if present


@dataclass
class RawExtracted:
    university: str
    title: str
    url: str
    source_page_url: str
    description: str
    content_kind: str
    published_date_iso: str | None
    published_date_raw: str | None


@dataclass
class NormalizedItem:
    university: str
    title: str
    description: str
    content_kind: str
    category: str
    url: str
    date: str
    published_date_raw: str | None
    date_confidence: DateConfidence
    scraped_at: str
    source_page_url: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "university": self.university,
            "title": self.title,
            "description": self.description,
            "content_kind": self.content_kind,
            "category": self.category,
            "url": self.url,
            "date": self.date,
            "published_date_raw": self.published_date_raw,
            "date_confidence": self.date_confidence,
            "scraped_at": self.scraped_at,
            "source_page_url": self.source_page_url,
        }

    def to_website_dict(self) -> dict[str, Any]:
        """Seven-bucket shape for public/data merge."""
        return {
            "university": self.university,
            "title": self.title,
            "url": self.url,
            "date": self.date,
            "category": self.category,
        }


@dataclass
class RunCounters:
    fetch_ok: int = 0
    fetch_failed: int = 0
    items_extracted: int = 0
    skipped_old: int = 0
    skipped_no_signal: int = 0
    skipped_duplicate: int = 0
    items_out: int = 0


@dataclass
class UniversityStats:
    name: str
    fetch_ok: int = 0
    fetch_failed: int = 0
    items_extracted: int = 0
    items_emitted: int = 0
