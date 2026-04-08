from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup

from parsers.base_parser import BaseParser, empty_categories, extract_date_near_anchor, iter_anchor_candidates_with_tags, raw_item


class RgpvParser(BaseParser):
    def parse(self, html: str, university: str, source_url: str) -> dict[str, list[dict[str, Any]]]:
        out = empty_categories()
        soup = BeautifulSoup(html, "html.parser")
        seen: set[str] = set()
        for abs_url, text, anchor in iter_anchor_candidates_with_tags(soup, source_url):
            low = text.lower()
            if "result" not in low and "exam" not in low:
                continue
            if abs_url in seen:
                continue
            seen.add(abs_url)
            d = extract_date_near_anchor(anchor)
            out["results"].append(raw_item(university, text[:500], abs_url, "results", date=d))
            if len(out["results"]) >= 25:
                break
        return out
