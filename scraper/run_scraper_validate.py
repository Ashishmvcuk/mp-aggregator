#!/usr/bin/env python3
"""Run live scraper then validate output (exit non-zero if validation fails)."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

SCRAPER_DIR = Path(__file__).resolve().parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict-run", action="store_true")
    ap.add_argument("--skip-website", action="store_true", help="Set SCRAPER_SKIP_WEBSITE_SYNC=1 for main.py")
    args = ap.parse_args()

    env = os.environ.copy()
    if args.skip_website:
        env["SCRAPER_SKIP_WEBSITE_SYNC"] = "1"

    r = subprocess.run([sys.executable, "main.py"], cwd=SCRAPER_DIR, env=env)
    if r.returncode != 0:
        return r.returncode

    cmd = [sys.executable, "validate_output.py"]
    if args.strict_run:
        cmd.append("--strict-run")
    r2 = subprocess.run(cmd, cwd=SCRAPER_DIR)
    return r2.returncode


if __name__ == "__main__":
    raise SystemExit(main())
