"""CLI entry for ``python -m scrapper_new``."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from scrapper_new.input_loader import DEFAULT_INPUT_REL
from scrapper_new.pipeline import run_pipeline

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent


def _output_dir_from_env(repo_root: Path) -> Path | None:
    """``SCRAPPER_NEW_OUTPUT_DIR``: absolute path, or path relative to repo root."""
    raw = os.environ.get("SCRAPPER_NEW_OUTPUT_DIR", "").strip()
    if not raw:
        return None
    p = Path(raw)
    return p.resolve() if p.is_absolute() else (repo_root / p).resolve()


def _setup_logging(log_dir: Path) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = log_dir / f"run_{ts}.log"

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    ch = logging.StreamHandler(sys.stderr)
    ch.setFormatter(fmt)
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(ch)
    root.addHandler(fh)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    return log_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scrape universities from input_data JSON.")
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help=f"Path to input JSON (default: <repo>/{DEFAULT_INPUT_REL})",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root (defaults to parent of scrapper_new/)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "Where to write input10_updates.json (default: scrapper_new/output/, "
            "or SCRAPPER_NEW_OUTPUT_DIR when set and this flag is omitted)"
        ),
    )
    parser.add_argument(
        "--emit-website-buckets",
        action="store_true",
        help="Also write website_buckets/*.json with canonical site shape.",
    )
    parser.add_argument(
        "--include-login-urls",
        action="store_true",
        help="Include student_login_url targets (default: skip).",
    )
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    input_path = (args.input or (repo_root / DEFAULT_INPUT_REL)).resolve()
    if args.output_dir is not None:
        output_dir = args.output_dir.resolve()
    else:
        from_env = _output_dir_from_env(repo_root)
        output_dir = from_env if from_env is not None else (PACKAGE_DIR / "output").resolve()
    log_dir = (PACKAGE_DIR / "logs").resolve()

    log_path = _setup_logging(log_dir)
    log = logging.getLogger("scrapper_new.run")
    log.info("Log file: %s", log_path)
    log.info("repo_root=%s input=%s output_dir=%s", repo_root, input_path, output_dir)

    if not input_path.is_file():
        log.error("Input file not found: %s", input_path)
        return 1

    run_pipeline(
        input_path=input_path,
        output_dir=output_dir,
        emit_website_buckets=args.emit_website_buckets,
        include_login=args.include_login_urls,
    )
    log.info("Wrote %s and run_summary.json", output_dir / "input10_updates.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
