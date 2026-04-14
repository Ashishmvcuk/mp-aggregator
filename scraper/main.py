from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from parsers.base_parser import ensure_category_keys
from parsers.registry import PARSER_REGISTRY
from utils.dedupe import dedupe_category
from utils.fetcher import fetch_html
from utils.file_ops import (
    ensure_directories,
    sync_category_to_website,
    sync_scrape_meta_to_website,
    sync_universities_directory_to_website,
    website_relative_data_path,
    write_category_output,
    write_history_snapshot,
    write_run_summary,
    write_scrape_meta,
)
from utils.logger import setup_logging
from utils.normalizer import CATEGORY_ORDER, normalize_item_for_category
from utils.validator import validate_category_bucket

logger = logging.getLogger("scraper.run")

SCRAPER_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = SCRAPER_ROOT / "config" / "universities.json"
FIXTURES_CONFIG_PATH = SCRAPER_ROOT / "tests" / "fixtures" / "fixtures_universities.json"


def load_universities() -> list[dict[str, Any]]:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("universities.json must be a JSON array")
    return data


def _entry_urls(entry: dict[str, Any]) -> list[str]:
    """Primary `url` plus optional `seed_urls` (deduped, order preserved)."""
    primary = str(entry.get("url", "")).strip()
    if not primary:
        return []
    out: list[str] = []
    seen: set[str] = set()
    seeds = entry.get("seed_urls")
    extra: list[str] = seeds if isinstance(seeds, list) else []
    for u in [primary] + extra:
        u = str(u).strip()
        if not u or u in seen:
            continue
        seen.add(u)
        out.append(u)
    return out


def _parser_names_for_entry(entry: dict[str, Any]) -> list[str]:
    """Single `parser` or list `parsers` (e.g. mp_portal + rgpv for result-heavy sites)."""
    raw = entry.get("parsers")
    if isinstance(raw, list) and raw:
        names = [str(x).strip().lower() for x in raw if str(x).strip()]
        return names if names else ["mp_portal"]
    name = str(entry.get("parser", "mp_portal")).strip().lower()
    return [name] if name else ["mp_portal"]


def _merge_category_dicts(parts: list[dict[str, Any]]) -> dict[str, Any]:
    merged: dict[str, list[dict[str, Any]]] = {c: [] for c in CATEGORY_ORDER}
    for p in parts:
        for c in CATEGORY_ORDER:
            merged[c].extend(p.get(c, []))
    return ensure_category_keys(merged)


def _skip_website_sync() -> bool:
    return os.environ.get("SCRAPER_SKIP_WEBSITE_SYNC", "").strip().lower() in ("1", "true", "yes")


def _finalize_pipeline(
    merged: dict[str, list[dict[str, Any]]],
    parsed_from_sources: dict[str, int],
    normalized_kept: dict[str, int],
    normalized_dropped: dict[str, int],
    run_id: str,
    run_ts: str,
    total: int,
    success_n: int,
    failed_n: int,
    failures: list[dict[str, str]],
    *,
    skip_website_sync: bool,
) -> dict[str, Any]:
    for cat in CATEGORY_ORDER:
        if normalized_dropped[cat] > 0:
            logger.warning(
                "[%s] %s: normalization dropped %d items (enable DEBUG for per-item detail)",
                run_id,
                cat,
                normalized_dropped[cat],
            )

    deduped: dict[str, list[dict[str, Any]]] = {}
    dedupe_removed: dict[str, int] = {c: 0 for c in CATEGORY_ORDER}
    for cat in CATEGORY_ORDER:
        deduped[cat], dedupe_removed[cat] = dedupe_category(cat, merged[cat])

    copy_status: dict[str, str] = {}
    categories_detail: dict[str, Any] = {}
    validation_status: dict[str, Any] = {}

    output_written = True
    for cat in CATEGORY_ORDER:
        outcome = validate_category_bucket(cat, deduped[cat])
        valid = outcome.valid_items
        validation_status[cat] = {
            "valid_count": len(valid),
            "error_count": len(outcome.errors),
            "errors_sample": outcome.errors[:5],
        }

        copy_reason = outcome.skip_reason
        status_label = "skipped"
        copy_err: str | None = None

        try:
            write_category_output(cat, valid)
            write_history_snapshot(cat, valid)
        except Exception as e:
            output_written = False
            logger.exception("[%s] Failed writing output for %s", run_id, cat)
            failures.append({"university": "*", "stage": "write", "message": f"{cat}: {e}"})

        if outcome.is_valid_for_copy:
            if skip_website_sync:
                status_label = "skipped_website_sync"
                copy_reason = "SCRAPER_SKIP_WEBSITE_SYNC"
                logger.info("[%s] Website sync disabled; skip %s", run_id, cat)
            else:
                try:
                    sync_category_to_website(cat, valid)
                    status_label = "copied"
                    copy_reason = "copied"
                except Exception as e:
                    status_label = f"error: {e}"
                    copy_err = str(e)
                    copy_reason = f"error: {e}"
                    logger.exception("[%s] Website sync failed for %s", run_id, cat)
                    failures.append({"university": "*", "stage": "copy", "message": f"{cat}: {e}"})
        else:
            if outcome.skip_reason == "has_errors":
                status_label = "skipped_invalid"
                copy_reason = "validation_errors"
            elif outcome.skip_reason == "empty":
                status_label = "skipped_empty"
                copy_reason = "empty_validated_list"
            elif outcome.skip_reason == "unknown_category":
                status_label = "skipped_invalid"
                copy_reason = "unknown_category"
            else:
                status_label = "skipped_empty"
                copy_reason = outcome.skip_reason
            logger.info(
                "[%s] Not copying %s: skip_reason=%s valid=%d errors=%d",
                run_id,
                cat,
                outcome.skip_reason,
                len(valid),
                len(outcome.errors),
            )

        copy_status[cat] = status_label

        categories_detail[cat] = {
            "parsed_from_sources": parsed_from_sources[cat],
            "normalized_kept": normalized_kept[cat],
            "normalized_dropped": normalized_dropped[cat],
            "after_dedupe": len(deduped[cat]),
            "dedupe_removed": dedupe_removed[cat],
            "validation_error_count": len(outcome.errors),
            "valid_for_output": len(valid),
            "copy_status": status_label,
            "copy_reason": copy_reason,
            "website_relative_path": website_relative_data_path(cat),
        }
        if copy_err:
            categories_detail[cat]["copy_error"] = copy_err

    unique_counts = {c: len(deduped[c]) for c in CATEGORY_ORDER}
    all_empty = all(len(deduped[c]) == 0 for c in CATEGORY_ORDER)

    for cat in CATEGORY_ORDER:
        logger.info(
            "[%s] Summary %s: parsed=%d norm_kept=%d norm_drop=%d dedupe_rm=%d valid_out=%d copy=%s",
            run_id,
            cat,
            parsed_from_sources[cat],
            normalized_kept[cat],
            normalized_dropped[cat],
            dedupe_removed[cat],
            categories_detail[cat]["valid_for_output"],
            copy_status[cat],
        )

    if not skip_website_sync:
        try:
            sync_universities_directory_to_website()
        except Exception as e:
            logger.exception("[%s] Website sync failed for universities directory", run_id)
            failures.append(
                {"university": "*", "stage": "copy", "message": f"universities.json: {e}"}
            )

    summary = {
        "run_id": run_id,
        "run_timestamp": run_ts,
        "universities_total": total,
        "universities_success": success_n,
        "universities_failed": failed_n,
        "raw_counts": parsed_from_sources,
        "unique_counts": unique_counts,
        "categories": categories_detail,
        "validation_status": validation_status,
        "copy_status": copy_status,
        "output_written": output_written,
        "all_categories_empty": all_empty,
        "failures": failures,
    }
    write_run_summary(summary)
    write_scrape_meta(summary)
    if not skip_website_sync:
        try:
            sync_scrape_meta_to_website()
        except Exception as e:
            logger.exception("[%s] Website sync failed for scrape_meta.json", run_id)
            failures.append(
                {"university": "*", "stage": "copy", "message": f"scrape_meta.json: {e}"}
            )
    logger.info(
        "[%s] Run finished: universities ok=%d fail=%d",
        run_id,
        success_n,
        failed_n,
    )
    return summary


def run_once() -> dict[str, Any]:
    setup_logging()
    ensure_directories()

    run_ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    logger.info("=== Scraper run %s | run_timestamp=%s ===", run_id, run_ts)

    skip_sync = _skip_website_sync()
    if skip_sync:
        logger.info("SCRAPER_SKIP_WEBSITE_SYNC is set — skipping writes to website/public/data/")

    universities = load_universities()
    enabled = [u for u in universities if u.get("enabled", True)]
    total = len(enabled)
    success_n = 0
    failed_n = 0
    failures: list[dict[str, str]] = []

    merged: dict[str, list[dict[str, Any]]] = {c: [] for c in CATEGORY_ORDER}
    parsed_from_sources: dict[str, int] = {c: 0 for c in CATEGORY_ORDER}
    normalized_kept: dict[str, int] = {c: 0 for c in CATEGORY_ORDER}
    normalized_dropped: dict[str, int] = {c: 0 for c in CATEGORY_ORDER}

    for entry in enabled:
        uni = str(entry.get("university", "")).strip()
        primary_url = str(entry.get("url", "")).strip()
        parser_names = _parser_names_for_entry(entry)
        unknown = [n for n in parser_names if n not in PARSER_REGISTRY]
        if unknown:
            failed_n += 1
            failures.append(
                {
                    "university": uni or "?",
                    "stage": "config",
                    "message": f"Unknown parser(s): {unknown!r}",
                }
            )
            logger.error("[%s] Unknown parser(s) %r for %s", run_id, unknown, uni)
            continue
        if not primary_url:
            failed_n += 1
            failures.append({"university": uni, "stage": "config", "message": "Missing url"})
            continue

        fetch_urls = _entry_urls(entry)
        if not fetch_urls:
            failed_n += 1
            failures.append({"university": uni, "stage": "config", "message": "No fetch URLs"})
            continue

        html_parts: list[tuple[str, str]] = []
        for fetch_url in fetch_urls:
            logger.info("[%s] Fetch: %s (%s)", run_id, uni, fetch_url)
            html = fetch_html(fetch_url)
            if html is not None:
                html_parts.append((fetch_url, html))
        if not html_parts:
            failed_n += 1
            failures.append(
                {"university": uni, "stage": "fetch", "message": "All fetch URLs failed or empty"}
            )
            continue

        parse_chunks: list[dict[str, Any]] = []
        parse_errors: list[str] = []
        for fetch_url, html in html_parts:
            for pname in parser_names:
                parser_cls = PARSER_REGISTRY[pname]
                try:
                    parser = parser_cls()
                    raw_parsed = parser.parse(html, uni, fetch_url)
                    parse_chunks.append(ensure_category_keys(raw_parsed))
                except Exception as e:
                    msg = f"{pname}@{fetch_url}: {type(e).__name__}: {e}"
                    parse_errors.append(msg)
                    logger.exception("[%s] Parse failed %s for %s", run_id, pname, uni)

        if not parse_chunks:
            failed_n += 1
            failures.append(
                {
                    "university": uni,
                    "stage": "parse",
                    "message": "; ".join(parse_errors) if parse_errors else "No successful parse",
                }
            )
            continue

        parsed = _merge_category_dicts(parse_chunks)

        for cat in CATEGORY_ORDER:
            bucket_items = parsed.get(cat, [])
            parsed_from_sources[cat] += len(bucket_items)
            for item in bucket_items:
                norm = normalize_item_for_category(item, primary_url, cat)
                if norm:
                    merged[cat].append(norm)
                    normalized_kept[cat] += 1
                else:
                    normalized_dropped[cat] += 1

        success_n += 1
        logger.info(
            "[%s] Parsed %s: %s",
            run_id,
            uni,
            {c: len(parsed.get(c, [])) for c in CATEGORY_ORDER},
        )

    return _finalize_pipeline(
        merged,
        parsed_from_sources,
        normalized_kept,
        normalized_dropped,
        run_id,
        run_ts,
        total,
        success_n,
        failed_n,
        failures,
        skip_website_sync=skip_sync,
    )


def run_fixtures(config_path: Path | None = None) -> dict[str, Any]:
    setup_logging()
    ensure_directories()

    run_ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_fixtures"

    logger.info("=== Fixture scraper run %s | run_timestamp=%s ===", run_id, run_ts)

    skip_sync = _skip_website_sync()
    if skip_sync:
        logger.info("SCRAPER_SKIP_WEBSITE_SYNC is set — skipping writes to website/public/data/")

    path = config_path or FIXTURES_CONFIG_PATH
    with open(path, encoding="utf-8") as f:
        entries = json.load(f)
    if not isinstance(entries, list):
        raise ValueError("fixtures config must be a JSON array")

    enabled = [e for e in entries if e.get("enabled", True)]
    total = len(enabled)
    success_n = 0
    failed_n = 0
    failures: list[dict[str, str]] = []

    merged: dict[str, list[dict[str, Any]]] = {c: [] for c in CATEGORY_ORDER}
    parsed_from_sources: dict[str, int] = {c: 0 for c in CATEGORY_ORDER}
    normalized_kept: dict[str, int] = {c: 0 for c in CATEGORY_ORDER}
    normalized_dropped: dict[str, int] = {c: 0 for c in CATEGORY_ORDER}

    for entry in enabled:
        uni = str(entry.get("university", "")).strip()
        parser_name = str(entry.get("parser", "")).strip().lower()
        html_file = str(entry.get("html_file", "")).strip()
        source_url = str(entry.get("source_url", "https://fixture.example/")).strip()

        parser_cls = PARSER_REGISTRY.get(parser_name)
        if not parser_cls or not html_file:
            failed_n += 1
            failures.append(
                {"university": uni or "?", "stage": "config", "message": "Missing parser or html_file"}
            )
            continue

        html_path = SCRAPER_ROOT / html_file
        if not html_path.is_file():
            failed_n += 1
            failures.append(
                {"university": uni, "stage": "fixture", "message": f"Missing HTML {html_path}"}
            )
            continue

        html = html_path.read_text(encoding="utf-8")
        try:
            parser = parser_cls()
            raw_parsed = parser.parse(html, uni, source_url)
            parsed = ensure_category_keys(raw_parsed)
        except Exception as e:
            failed_n += 1
            failures.append(
                {"university": uni, "stage": "parse", "message": f"{type(e).__name__}: {e}"}
            )
            logger.exception("[%s] Fixture parse failed for %s", run_id, uni)
            continue

        for cat in CATEGORY_ORDER:
            bucket_items = parsed.get(cat, [])
            parsed_from_sources[cat] += len(bucket_items)
            for item in bucket_items:
                norm = normalize_item_for_category(item, source_url, cat)
                if norm:
                    merged[cat].append(norm)
                    normalized_kept[cat] += 1
                else:
                    normalized_dropped[cat] += 1

        success_n += 1
        logger.info("[%s] Fixture parsed %s", run_id, uni)

    return _finalize_pipeline(
        merged,
        parsed_from_sources,
        normalized_kept,
        normalized_dropped,
        run_id,
        run_ts,
        total,
        success_n,
        failed_n,
        failures,
        skip_website_sync=skip_sync,
    )


def main() -> None:
    run_once()


if __name__ == "__main__":
    main()
