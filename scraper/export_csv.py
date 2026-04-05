#!/usr/bin/env python3
"""Optional CSV export from scraper/output/*.json into scraper/output/csv/."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from utils.file_ops import OUTPUT_DIR, OUTPUT_CSV_DIR
from utils.normalizer import CATEGORY_ORDER


def main() -> int:
    parser = argparse.ArgumentParser(description="Export category JSON to CSV.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--csv-dir", type=Path, default=OUTPUT_CSV_DIR)
    args = parser.parse_args()

    args.csv_dir.mkdir(parents=True, exist_ok=True)
    fields = ["university", "title", "url", "date", "category"]

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
                    w.writerow({k: row.get(k, "") for k in fields})
        print(f"wrote {csv_path} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
