from __future__ import annotations

from utils.validator import validate_category_bucket


def test_validate_accepts_null_announcement_date_with_index() -> None:
    items = [
        {
            "university": "U",
            "title": "Notice",
            "url": "https://example.edu/n",
            "date": None,
            "category": "news",
            "scrape_index_date": "2026-04-15",
        }
    ]
    out = validate_category_bucket("news", items)
    assert out.is_valid_for_copy
    assert len(out.valid_items) == 1
    assert out.valid_items[0]["date"] is None


def test_validate_rejects_bad_scrape_index_date() -> None:
    items = [
        {
            "university": "U",
            "title": "Notice",
            "url": "https://example.edu/n",
            "date": None,
            "category": "news",
            "scrape_index_date": "not-a-date",
        }
    ]
    out = validate_category_bucket("news", items)
    assert not out.is_valid_for_copy
