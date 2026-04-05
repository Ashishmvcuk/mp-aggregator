#!/usr/bin/env python3
"""Run pipeline against HTML fixtures (no network)."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRAPER_DIR = Path(__file__).resolve().parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=None)
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--strict-run", action="store_true")
    args = ap.parse_args()

    from main import run_fixtures

    run_fixtures(args.config)

    if args.validate:
        cmd = [sys.executable, "validate_output.py"]
        if args.strict_run:
            cmd.append("--strict-run")
        return subprocess.run(cmd, cwd=SCRAPER_DIR).returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
