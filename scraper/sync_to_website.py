#!/usr/bin/env python3
"""Copy validated non-empty category JSON from scraper/output to website/public/data/."""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from utils.file_ops import (
    OUTPUT_DIR,
    WEBSITE_DATA_DIR,
    safe_write_json,
    sync_category_to_website,
    sync_universities_directory_to_website,
)
from utils.logger import setup_logging
from utils.normalizer import CATEGORY_ORDER
from utils.validator import validate_category_bucket

logger = logging.getLogger("scraper.sync")


def sync_scrape_meta(output_dir: Path) -> bool:
    meta_path = output_dir / "scrape_meta.json"
    if not meta_path.is_file():
        logger.warning("Missing scrape_meta.json — skip (incomplete run?)")
        return True
    try:
        with open(meta_path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error("scrape_meta.json: invalid (%s)", e)
        return False
    if not isinstance(data, dict):
        logger.error("scrape_meta.json: root must be a JSON object")
        return False
    try:
        safe_write_json(WEBSITE_DATA_DIR / "scrape_meta.json", data)
    except Exception:
        logger.exception("Failed writing scrape_meta to website/public/data/")
        return False
    logger.info("Synced scrape_meta.json")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync validated output JSON to website/public/data/")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    setup_logging()

    failed = False
    for cat in CATEGORY_ORDER:
        path = args.output_dir / f"{cat}.json"
        if not path.is_file():
            logger.warning("Missing %s — skip", path.name)
            continue
        with open(path, encoding="utf-8") as f:
            items = json.load(f)
        if not isinstance(items, list):
            logger.error("%s: not a JSON array", path)
            failed = True
            continue
        outcome = validate_category_bucket(cat, items)
        if not outcome.is_valid_for_copy:
            logger.info(
                "Skip %s: not copying (reason=%s valid=%d errors=%d)",
                cat,
                outcome.skip_reason,
                len(outcome.valid_items),
                len(outcome.errors),
            )
            continue
        try:
            sync_category_to_website(cat, outcome.valid_items)
        except Exception as e:
            logger.exception("Sync failed for %s", cat)
            failed = True
    if not sync_scrape_meta(args.output_dir):
        failed = True
    try:
        sync_universities_directory_to_website()
    except Exception as e:
        logger.exception("Failed syncing universities directory: %s", e)
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
