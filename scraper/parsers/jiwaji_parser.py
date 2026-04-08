from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from parsers.base_parser import BaseParser, empty_categories, extract_date_near_anchor, iter_anchor_candidates_with_tags, raw_item


class JiwajiParser(BaseParser):
    def parse(self, html: str, university: str, source_url: str) -> dict[str, list[dict[str, Any]]]:
        out = empty_categories()
        soup = BeautifulSoup(html, "html.parser")
        seen: set[str] = set()
        for abs_url, text, anchor in iter_anchor_candidates_with_tags(soup, source_url):
            low = text.lower()
            if "syllabus" in low:
                bucket = "syllabus"
            elif "admit" in low or "hall ticket" in low:
                bucket = "admit_cards"
            elif "result" in low or "exam" in low:
                bucket = "results"
            else:
                continue
            if abs_url in seen:
                continue
            seen.add(abs_url)
            d = extract_date_near_anchor(anchor)
            out[bucket].append(raw_item(university, text[:500], abs_url, bucket, date=d))
            if sum(len(out[k]) for k in out) >= 25:
                break
        if not any(out.values()):
            out["results"] = [
                raw_item(
                    university,
                    "[MOCK] Sample Jiwaji pipeline row — replace with real selectors",
                    urljoin(source_url, "/"),
                    "results",
                )
            ]
        return out
