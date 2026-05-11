#!/usr/bin/env python3
"""
Copy scrapper_new website bucket JSON into the Vite public ``data/`` folder (flat),
and refresh ``scrape_meta.json`` so the site header shows **Last run**.

Default source:
  ``<repo>/scrapper_new/output/website_buckets/*.json``, unless ``SCRAPPER_NEW_OUTPUT_DIR``
  is set — then ``<that>/website_buckets/*.json``. ``run_summary.json`` is read from the
  parent of the bucket directory.

Dest: ``<repo>/website/public/data/*.json`` (same filenames: news.json, …).

Run after ``python3 -m scrapper_new --emit-website-buckets`` (matching output layout).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SOURCE = REPO_ROOT / "scrapper_new" / "output" / "website_buckets"
DEFAULT_DEST = REPO_ROOT / "website" / "public" / "data"


def _output_dir_from_env(repo_root: Path) -> Path | None:
    """``SCRAPPER_NEW_OUTPUT_DIR``: absolute path, or path relative to repo root."""
    raw = os.environ.get("SCRAPPER_NEW_OUTPUT_DIR", "").strip()
    if not raw:
        return None
    p = Path(raw)
    return p.resolve() if p.is_absolute() else (repo_root / p).resolve()


def _utc_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_scrapper_new_version(repo_root: Path) -> str:
    p = repo_root / "scrapper_new" / "__init__.py"
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return "0.0.0"
    m = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', text, re.M)
    return m.group(1).strip() if m else "0.0.0"


def _read_site_package_version(repo_root: Path) -> str:
    p = repo_root / "website" / "package.json"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        v = data.get("version")
        return str(v).strip() if v is not None else "0.0.0"
    except (OSError, json.JSONDecodeError, TypeError):
        return "0.0.0"


def _read_run_summary(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _category_counts(dest: Path, feed_names: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for name in feed_names:
        p = dest / name
        if not p.is_file():
            continue
        key = name.replace(".json", "")
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            counts[key] = len(data) if isinstance(data, list) else 0
        except (OSError, json.JSONDecodeError):
            counts[key] = 0
    return counts


def write_scrape_meta(
    *,
    dest: Path,
    repo_root: Path,
    run_summary_path: Path | None,
    feed_filenames: list[str],
) -> Path:
    """Write ``website/public/data/scrape_meta.json`` (shape expected by CI + Header)."""
    now_z = _utc_z()
    summary = _read_run_summary(run_summary_path) if run_summary_path else None

    scraped_at = now_z
    run_started = now_z
    run_id = f"scrapper_new_{now_z.replace(':', '').replace('-', '')}"
    if summary:
        completed = summary.get("run_completed_at")
        if isinstance(completed, str) and completed.strip():
            scraped_at = completed.strip()
        started = summary.get("run_started_at")
        if isinstance(started, str) and started.strip():
            run_started = started.strip()
        rid = summary.get("run_id")
        if isinstance(rid, str) and rid.strip():
            run_id = rid.strip()

    meta_path = dest / "scrape_meta.json"
    payload: dict = {
        "scrapedAt": scraped_at,
        "websiteSyncAt": now_z,
        "runStartedAt": run_started,
        "runId": run_id,
        "scraperVersion": f"scrapper_new-{_read_scrapper_new_version(repo_root)}",
        "siteReleaseVersion": _read_site_package_version(repo_root),
        "source": "scrapper_new",
        "categoryCounts": _category_counts(dest, feed_filenames),
    }
    ci = os.environ.get("SCRAPPER_NEW_CI_RUN_ID", "").strip() or os.environ.get("SCRAPER_CI_RUN_ID", "").strip()
    if ci:
        payload["ciRunId"] = ci

    meta_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {meta_path} (Last run / websiteSyncAt)")
    return meta_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root (default: inferred from script location)",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=None,
        help=(
            "Website buckets directory (default: <SCRAPPER_NEW_OUTPUT_DIR>/website_buckets if set, "
            "else scrapper_new/output/website_buckets)"
        ),
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=None,
        help=f"Destination: website public data dir (default: {DEFAULT_DEST.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "--run-summary",
        type=Path,
        default=None,
        help="Optional run_summary.json (default: <parent of source>/run_summary.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions only; do not write files",
    )
    args = parser.parse_args()
    root = args.repo_root.resolve()
    if args.source is not None:
        src = args.source.resolve()
    else:
        env_base = _output_dir_from_env(root)
        if env_base is not None:
            src = (env_base / "website_buckets").resolve()
        else:
            src = (root / "scrapper_new" / "output" / "website_buckets").resolve()
    dest = (args.dest or (root / "website" / "public" / "data")).resolve()
    if args.run_summary is not None:
        run_summary = args.run_summary.resolve()
    else:
        run_summary = (src.parent / "run_summary.json").resolve()

    if not src.is_dir():
        print(f"::error::Source directory missing: {src}", file=sys.stderr)
        print("Run: python3 -m scrapper_new --emit-website-buckets", file=sys.stderr)
        return 1

    json_files = sorted(src.glob("*.json"))
    if not json_files:
        print(f"::error::No *.json under {src}", file=sys.stderr)
        return 1

    feed_names = [p.name for p in json_files]

    if args.dry_run:
        print(f"Would copy {len(json_files)} file(s) from {src} -> {dest}/")
        for p in json_files:
            print(f"  {p.name}")
        print(f"Would write scrape_meta.json (run_summary={run_summary})")
        return 0

    dest.mkdir(parents=True, exist_ok=True)
    copied = 0
    for path in json_files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"::error::Invalid JSON {path}: {e}", file=sys.stderr)
            return 1
        if not isinstance(data, list):
            print(f"::error::{path.name}: root must be a JSON array", file=sys.stderr)
            return 1
        target = dest / path.name
        shutil.copy2(path, target)
        copied += 1
        print(f"copied {path.name} ({len(data)} rows) -> {target}")

    rs_path = run_summary if run_summary.is_file() else None
    write_scrape_meta(dest=dest, repo_root=root, run_summary_path=rs_path, feed_filenames=feed_names)

    print(f"OK: {copied} feed file(s) + scrape_meta.json -> {dest}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
