from __future__ import annotations

from parsers.base_parser import ensure_category_keys, raw_item
from main import _entry_urls, _merge_category_dicts, _parser_names_for_entry


def test_entry_urls_primary_and_seeds_dedupe():
    assert _entry_urls({"url": "https://a.edu/", "seed_urls": ["https://a.edu/", "https://b.edu/"]}) == [
        "https://a.edu/",
        "https://b.edu/",
    ]


def test_entry_urls_missing_primary():
    assert _entry_urls({"seed_urls": ["https://b.edu/"]}) == []


def test_parser_names_single():
    assert _parser_names_for_entry({"parser": "mp_portal"}) == ["mp_portal"]


def test_parser_names_list():
    assert _parser_names_for_entry({"parsers": ["mp_portal", "rgpv"]}) == ["mp_portal", "rgpv"]


def test_merge_category_dicts():
    a = ensure_category_keys({"results": [raw_item("U", "R1", "https://x/1", "results")]})
    b = ensure_category_keys({"news": [raw_item("U", "N1", "https://x/2", "news")]})
    m = _merge_category_dicts([a, b])
    assert len(m["results"]) == 1
    assert len(m["news"]) == 1
