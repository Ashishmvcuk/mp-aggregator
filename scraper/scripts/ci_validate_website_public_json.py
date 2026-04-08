#!/usr/bin/env python3
"""Ensure every *.json under website/public/data/ is valid JSON and a top-level array (CI safety)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "website" / "public" / "data"

# Category feeds are JSON arrays; scrape_meta is a single object for the UI.
META_OBJECT_FILES = frozenset({"scrape_meta.json"})
SCRAPE_META_REQUIRED_KEYS = frozenset(
    {"scrapedAt", "runId", "scraperVersion", "siteReleaseVersion"}
)

MANUAL_ADDITIONS_FILE = "manual_additions.json"
MANUAL_CATEGORY_KEYS = frozenset(
    {"results", "news", "jobs", "syllabus", "admit_cards", "blogs", "enrollments"}
)
UNIVERSITIES_FILE = "universities.json"


def main() -> int:
    if not DATA_DIR.is_dir():
        print(f"::error::Missing directory {DATA_DIR}")
        return 1
    paths = sorted(DATA_DIR.glob("*.json"))
    if not paths:
        print("::warning::No JSON files under website/public/data (nothing to validate)")
        return 0
    failed = False
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8")
            data = json.loads(text)
        except (OSError, json.JSONDecodeError) as e:
            print(f"::error::{p.relative_to(REPO_ROOT)}: invalid JSON ({e})")
            failed = True
            continue
        if p.name in META_OBJECT_FILES:
            if not isinstance(data, dict):
                print(f"::error::{p.relative_to(REPO_ROOT)}: root must be a JSON object")
                failed = True
                continue
            missing = SCRAPE_META_REQUIRED_KEYS - data.keys()
            if missing:
                print(
                    f"::error::{p.relative_to(REPO_ROOT)}: scrape_meta missing keys {sorted(missing)}"
                )
                failed = True
        elif p.name == MANUAL_ADDITIONS_FILE:
            if not isinstance(data, dict):
                print(f"::error::{p.relative_to(REPO_ROOT)}: root must be a JSON object")
                failed = True
                continue
            unknown = set(data.keys()) - MANUAL_CATEGORY_KEYS
            if unknown:
                print(
                    f"::error::{p.relative_to(REPO_ROOT)}: manual_additions unknown keys {sorted(unknown)}"
                )
                failed = True
            missing_keys = MANUAL_CATEGORY_KEYS - set(data.keys())
            if missing_keys:
                print(
                    f"::error::{p.relative_to(REPO_ROOT)}: manual_additions missing keys {sorted(missing_keys)}"
                )
                failed = True
            for key in MANUAL_CATEGORY_KEYS:
                if not isinstance(data[key], list):
                    print(
                        f"::error::{p.relative_to(REPO_ROOT)}: manual_additions[{key!r}] must be a JSON array"
                    )
                    failed = True
        elif p.name == UNIVERSITIES_FILE:
            if not isinstance(data, list):
                print(f"::error::{p.relative_to(REPO_ROOT)}: root must be a JSON array")
                failed = True
                continue
            for i, row in enumerate(data):
                if not isinstance(row, dict):
                    print(
                        f"::error::{p.relative_to(REPO_ROOT)}: universities[{i}] must be an object"
                    )
                    failed = True
                    continue
                u, url = row.get("university"), row.get("url")
                if not isinstance(u, str) or not u.strip():
                    print(
                        f"::error::{p.relative_to(REPO_ROOT)}: universities[{i}]: missing non-empty university"
                    )
                    failed = True
                if not isinstance(url, str) or not url.strip():
                    print(
                        f"::error::{p.relative_to(REPO_ROOT)}: universities[{i}]: missing non-empty url"
                    )
                    failed = True
                g = row.get("group")
                if g is not None and not isinstance(g, str):
                    print(
                        f"::error::{p.relative_to(REPO_ROOT)}: universities[{i}]: group must be a string if present"
                    )
                    failed = True
        elif not isinstance(data, list):
            print(f"::error::{p.relative_to(REPO_ROOT)}: root must be a JSON array")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
