from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from parsers.base_parser import BaseParser, empty_categories, iter_anchor_candidates, raw_item


class RgpvParser(BaseParser):
    def parse(self, html: str, university: str, source_url: str) -> dict[str, list[dict[str, Any]]]:
        out = empty_categories()
        soup = BeautifulSoup(html, "html.parser")
        seen: set[str] = set()
        for abs_url, text in iter_anchor_candidates(soup, source_url):
            low = text.lower()
            if "result" not in low and "exam" not in low:
                continue
            if abs_url in seen:
                continue
            seen.add(abs_url)
            out["results"].append(raw_item(university, text[:500], abs_url, "results"))
            if len(out["results"]) >= 25:
                break
        if not out["results"]:
            out["results"] = [
                raw_item(
                    university,
                    "[MOCK] Sample RGPV pipeline row — replace with real selectors",
                    urljoin(source_url, "/Result/frmStudentResult.aspx"),
                    "results",
                )
            ]
        return out
