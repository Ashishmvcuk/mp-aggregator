from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from parsers.base_parser import BaseParser, empty_categories, iter_anchor_candidates, raw_item


class DavvParser(BaseParser):
    def parse(self, html: str, university: str, source_url: str) -> dict[str, list[dict[str, Any]]]:
        out = empty_categories()
        soup = BeautifulSoup(html, "html.parser")
        seen: set[str] = set()
        for abs_url, text in iter_anchor_candidates(soup, source_url):
            low = text.lower()
            if not any(k in low for k in ("result", "exam", "notice", "circular")):
                continue
            if abs_url in seen:
                continue
            seen.add(abs_url)
            bucket = "news" if "notice" in low or "circular" in low else "results"
            out[bucket].append(raw_item(university, text[:500], abs_url, bucket))
            if len(out["results"]) + len(out["news"]) >= 25:
                break
        if not out["results"] and not out["news"]:
            out["results"] = [
                raw_item(
                    university,
                    "[MOCK] Sample DAVV pipeline row — replace with real selectors",
                    urljoin(source_url, "/"),
                    "results",
                )
            ]
        return out
