#!/usr/bin/env python3
"""POST run_summary.json (and optional scrape_meta) to SCRAPER_WEBHOOK_URL if set. No secrets in repo."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

SCRAPER_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    url = os.environ.get("SCRAPER_WEBHOOK_URL", "").strip()
    if not url:
        print("SCRAPER_WEBHOOK_URL not set — skip webhook")
        return 0

    summary_path = SCRAPER_ROOT / "output" / "run_summary.json"
    meta_path = SCRAPER_ROOT / "output" / "scrape_meta.json"
    payload: dict = {}
    if summary_path.is_file():
        payload["run_summary"] = json.loads(summary_path.read_text(encoding="utf-8"))
    if meta_path.is_file():
        payload["scrape_meta"] = json.loads(meta_path.read_text(encoding="utf-8"))
    if not payload:
        print("::warning::No output JSON to send — skip webhook")
        return 0

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            print(f"Webhook POST OK: HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        print(f"::warning::Webhook HTTP error: {e.code} {e.reason}")
        return 0
    except urllib.error.URLError as e:
        print(f"::warning::Webhook URL error: {e}")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
