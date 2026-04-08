#!/usr/bin/env python3
"""Fail CI if scraper run_summary shows too many university fetch/parse failures (optional thresholds via env)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SCRAPER_ROOT = Path(__file__).resolve().parent.parent
SUMMARY = SCRAPER_ROOT / "output" / "run_summary.json"


def main() -> int:
    if not SUMMARY.is_file():
        print("::warning::run_summary.json missing — skip health check")
        return 0
    try:
        data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"::error::Cannot read run_summary.json: {e}")
        return 1
    total = int(data.get("universities_total") or 0)
    failed = int(data.get("universities_failed") or 0)
    ok = int(data.get("universities_success") or 0)

    max_fail = os.environ.get("SCRAPER_MAX_UNIVERSITY_FAILURES", "").strip()
    max_ratio = os.environ.get("SCRAPER_MAX_FAILURE_RATIO", "").strip()

    if max_fail:
        try:
            cap = int(max_fail)
            if failed > cap:
                print(
                    f"::error::Scraper health: universities_failed={failed} exceeds SCRAPER_MAX_UNIVERSITY_FAILURES={cap}"
                )
                return 1
        except ValueError:
            print("::warning::Invalid SCRAPER_MAX_UNIVERSITY_FAILURES — ignored")

    if max_ratio and total > 0:
        try:
            r = float(max_ratio)
            if failed / total > r:
                print(
                    f"::error::Scraper health: failure ratio {failed}/{total} exceeds SCRAPER_MAX_FAILURE_RATIO={r}"
                )
                return 1
        except ValueError:
            print("::warning::Invalid SCRAPER_MAX_FAILURE_RATIO — ignored")

    print(
        f"Scraper health OK: success={ok} failed={failed} total={total} "
        f"(thresholds: max_failures={max_fail or '—'} max_ratio={max_ratio or '—'})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
