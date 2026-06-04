#!/usr/bin/env python3
"""Optional: copy ``input_data/syllabus.json`` → ``website/public/data/syllabus_input.json``.

Not run by scrapers or Vite. Use only when you maintain a copy in input_data/ and want
to push it to the public folder before build.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE = REPO_ROOT / "input_data" / "syllabus.json"
DEST = REPO_ROOT / "website" / "public" / "data" / "syllabus_input.json"


def main() -> int:
    if not SOURCE.is_file():
        print(f"missing source: {SOURCE}", file=sys.stderr)
        return 1
    try:
        data = json.loads(SOURCE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"invalid {SOURCE}: {e}", file=sys.stderr)
        return 1
    if not isinstance(data, list):
        print(f"{SOURCE} must be a JSON array", file=sys.stderr)
        return 1
    DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, DEST)
    print(f"synced {len(data)} rows -> {DEST.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
