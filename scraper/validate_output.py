#!/usr/bin/env python3
"""Validate scraper/output/*.json. Exit 0 on success, 1 on failure."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from utils.file_ops import OUTPUT_DIR
from utils.output_validator import validate_output_directory


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate scraper output JSON files.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument(
        "--strict-run",
        action="store_true",
        help="Fail if run_summary shows university success but all categories empty",
    )
    args = parser.parse_args()

    report = validate_output_directory(args.output_dir, strict_run=args.strict_run)

    for cat, cr in report.categories.items():
        status = "OK" if cr.valid else "FAIL"
        dup = f" dup_removed={cr.duplicate_rows_removed}" if cr.duplicate_rows_removed else ""
        print(f"[{status}] {cat}: items={cr.item_count}{dup}")
        for e in cr.errors[:5]:
            print(f"       {e}")
        if len(cr.errors) > 5:
            print(f"       ... ({len(cr.errors) - 5} more)")

    for e in report.global_errors:
        print(f"ERROR: {e}", file=sys.stderr)

    all_cat_ok = all(cr.valid for cr in report.categories.values())
    if report.ok and all_cat_ok:
        print("Validation passed.")
        return 0
    print("Validation failed.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
