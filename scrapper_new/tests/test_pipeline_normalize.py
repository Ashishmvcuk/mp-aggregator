from datetime import date

from scrapper_new.models import RawExtracted
from scrapper_new.pipeline import normalize_row


def _raw(title: str, published: str | None = None, kind: str = "news") -> RawExtracted:
    return RawExtracted(
        university="Test University",
        title=title,
        url="https://example.edu/notice/1",
        source_page_url="https://example.edu/news",
        description="",
        content_kind=kind,
        published_date_iso=published,
        published_date_raw=published,
    )


def test_normalize_high_confidence_recent():
    today = date(2026, 5, 11)
    cutoff = date(2026, 3, 12)
    item, skip = normalize_row(
        _raw("Exam form", "2026-05-01"),
        source_page_url="https://example.edu/n",
        page_last_modified=None,
        cutoff=cutoff,
        scraped_at_iso="2026-05-11T12:00:00+00:00",
        today_utc=today,
    )
    assert skip is None
    assert item is not None
    assert item.date == "2026-05-01"
    assert item.date_confidence == "high"


def test_normalize_drops_old():
    today = date(2026, 5, 11)
    cutoff = date(2026, 3, 12)
    item, skip = normalize_row(
        _raw("Old", "2020-01-01"),
        source_page_url="https://example.edu/n",
        page_last_modified=None,
        cutoff=cutoff,
        scraped_at_iso="2026-05-11T12:00:00+00:00",
        today_utc=today,
    )
    assert item is None
    assert skip == "old"


def test_normalize_medium_last_modified():
    today = date(2026, 5, 11)
    cutoff = date(2026, 3, 12)
    item, skip = normalize_row(
        _raw("Some notice without inline date", None),
        source_page_url="https://example.edu/n",
        page_last_modified=date(2026, 4, 20),
        cutoff=cutoff,
        scraped_at_iso="2026-05-11T12:00:00+00:00",
        today_utc=today,
    )
    assert skip is None
    assert item is not None
    assert item.date == "2026-04-20"
    assert item.date_confidence == "medium"


def test_normalize_low_year_in_title():
    today = date(2026, 5, 11)
    cutoff = date(2026, 3, 12)
    item, skip = normalize_row(
        _raw("Circular regarding exams 2026", None),
        source_page_url="https://example.edu/n",
        page_last_modified=date(2020, 1, 1),
        cutoff=cutoff,
        scraped_at_iso="2026-05-11T12:00:00+00:00",
        today_utc=today,
    )
    assert skip is None
    assert item is not None
    assert item.date == "2026-05-11"
    assert item.date_confidence == "low"


def test_normalize_no_signal():
    today = date(2026, 5, 11)
    cutoff = date(2026, 3, 12)
    item, skip = normalize_row(
        _raw("Home", None),
        source_page_url="https://example.edu/n",
        page_last_modified=date(2020, 1, 1),
        cutoff=cutoff,
        scraped_at_iso="2026-05-11T12:00:00+00:00",
        today_utc=today,
    )
    assert item is None
    assert skip == "no_signal"
