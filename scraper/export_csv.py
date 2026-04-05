#!/usr/bin/env python3
"""Optional CSV export from scraper/output/*.json into scraper/output/csv/."""
from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from utils.file_ops import OUTPUT_DIR, OUTPUT_CSV_DIR
from utils.normalizer import CATEGORY_ORDER

_DATE_HEAD = re.compile(r"^(\d{4}-\d{2}-\d{2})")


def row_date_time_iso(date_val: str) -> str:
    """Turn YYYY-MM-DD into ISO datetime (noon UTC) for CSV date_time column."""
    if not date_val or not isinstance(date_val, str):
        return ""
    m = _DATE_HEAD.match(date_val.strip())
    if not m:
        return ""
    return f"{m.group(1)}T12:00:00Z"


def main() -> int:
    parser = argparse.ArgumentParser(description="Export category JSON to CSV.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--csv-dir", type=Path, default=OUTPUT_CSV_DIR)
    args = parser.parse_args()

    args.csv_dir.mkdir(parents=True, exist_ok=True)
    exported_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    fields = ["university", "title", "url", "date", "date_time", "category", "exported_at"]

    for cat in CATEGORY_ORDER:
        jpath = args.output_dir / f"{cat}.json"
        if not jpath.is_file():
            print(f"skip {cat}: missing {jpath}")
            continue
        with open(jpath, encoding="utf-8") as f:
            rows = json.load(f)
        if not isinstance(rows, list):
            print(f"skip {cat}: not a JSON array")
            continue
        csv_path = args.csv_dir / f"{cat}.csv"
        with open(csv_path, "w", encoding="utf-8", newline="") as cf:
            w = csv.DictWriter(cf, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            for row in rows:
                if isinstance(row, dict):
                    d = row.get("date", "") or ""
                    w.writerow(
                        {
                            "university": row.get("university", ""),
                            "title": row.get("title", ""),
                            "url": row.get("url", ""),
                            "date": d,
                            "date_time": row_date_time_iso(str(d)),
                            "category": row.get("category", ""),
                            "exported_at": exported_at,
                        }
                    )
        print(f"wrote {csv_path} ({len(rows)} rows) exported_at={exported_at}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
