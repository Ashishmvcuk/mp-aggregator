#!/usr/bin/env python3
"""Ensure every *.json under website/public/data/ is valid JSON and a top-level array (CI safety)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "website" / "public" / "data"


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
        if not isinstance(data, list):
            print(f"::error::{p.relative_to(REPO_ROOT)}: root must be a JSON array")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
