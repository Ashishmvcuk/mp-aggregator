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
from utils.fetcher import fetch_html_detailed
from utils.file_ops import (
    ensure_directories,
    sync_category_to_website,
    sync_scrape_meta_to_website,
    sync_universities_directory_to_website,
    website_relative_data_path,
    write_category_output,
    write_fetch_url_audit_logs,
    write_history_snapshot,
    write_processing_exception_logs,
    write_run_summary,
    write_scrape_item_jsonl,
    write_scrape_meta,
)
from utils.logger import attach_run_log_file, detach_run_log_file, setup_logging
from utils.normalizer import CATEGORY_ORDER, normalize_item_for_category
from utils.recency import (
    cutoff_date_for_run,
    item_json_log_enabled,
    keep_item_for_recency,
    recency_days_from_env,
)
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


def _neutral_recency_summary() -> dict[str, Any]:
    return {
        "enabled": False,
        "days": None,
        "cutoff_iso": None,
        "dropped_by_category": {c: 0 for c in CATEGORY_ORDER},
        "total_dropped": 0,
    }


def _neutral_fetch_audit_summary() -> dict[str, Any]:
    return {
        "success_count": 0,
        "failure_count": 0,
        "processing_exceptions_count": 0,
        "logs": {
            "success_dir": "logs/success/",
            "failure_dir": "logs/failure/",
            "success_fetch_latest": "logs/success/fetch_urls_latest.jsonl",
            "failure_fetch_latest": "logs/failure/fetch_urls_latest.jsonl",
            "failure_processing_latest": "logs/failure/processing_exceptions_latest.jsonl",
        },
    }


def _run_log_relative_path(run_id: str) -> str:
    """Path under scraper/ root for run_summary / docs."""
    return f"logs/runs/scraper_{run_id}.log"


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
    recency: dict[str, Any] | None = None,
    fetch_audit: dict[str, Any] | None = None,
    run_log_file: str | None = None,
) -> dict[str, Any]:
    recency_block = recency if recency is not None else _neutral_recency_summary()
    recency_by_cat: dict[str, int] = recency_block.get("dropped_by_category") or {}
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
            "recency_dropped": int(recency_by_cat.get(cat, 0)),
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
            "[%s] Summary %s: parsed=%d norm_kept=%d norm_drop=%d recency_drop=%d dedupe_rm=%d valid_out=%d copy=%s",
            run_id,
            cat,
            parsed_from_sources[cat],
            normalized_kept[cat],
            normalized_dropped[cat],
            int(recency_by_cat.get(cat, 0)),
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
        "run_log_file": run_log_file,
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
        "recency": recency_block,
        "fetch_audit": fetch_audit if fetch_audit is not None else _neutral_fetch_audit_summary(),
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
    run_log_rel = _run_log_relative_path(run_id)
    run_file_handler = attach_run_log_file(run_id)

    try:
        logger.info("=== Scraper run %s | run_timestamp=%s ===", run_id, run_ts)
        logger.info("[%s] Per-run log file: %s", run_id, run_log_rel)

        skip_sync = _skip_website_sync()
        if skip_sync:
            logger.info("SCRAPER_SKIP_WEBSITE_SYNC is set — skipping writes to website/public/data/")

        try:
            universities = load_universities()
        except Exception as e:
            logger.exception("[%s] Failed to load universities config: %s", run_id, e)
            fail = [{"university": "*", "stage": "config", "message": f"{type(e).__name__}: {e}"}]
            try:
                write_fetch_url_audit_logs(run_id, [], [])
            except Exception as w:
                logger.warning("[%s] Could not write fetch audit logs: %s", run_id, w)
            try:
                write_processing_exception_logs(run_id, [])
            except Exception as w:
                logger.warning("[%s] Could not write processing exception logs: %s", run_id, w)
            return _finalize_pipeline(
                {c: [] for c in CATEGORY_ORDER},
                {c: 0 for c in CATEGORY_ORDER},
                {c: 0 for c in CATEGORY_ORDER},
                {c: 0 for c in CATEGORY_ORDER},
                run_id,
                run_ts,
                0,
                0,
                1,
                fail,
                skip_website_sync=skip_sync,
                recency=_neutral_recency_summary(),
                fetch_audit=_neutral_fetch_audit_summary(),
                run_log_file=run_log_rel,
            )

        enabled = [u for u in universities if u.get("enabled", True)]
        total = len(enabled)
        success_n = 0
        failed_n = 0
        failures: list[dict[str, str]] = []

        merged: dict[str, list[dict[str, Any]]] = {c: [] for c in CATEGORY_ORDER}
        parsed_from_sources: dict[str, int] = {c: 0 for c in CATEGORY_ORDER}
        normalized_kept: dict[str, int] = {c: 0 for c in CATEGORY_ORDER}
        normalized_dropped: dict[str, int] = {c: 0 for c in CATEGORY_ORDER}
        recency_dropped: dict[str, int] = {c: 0 for c in CATEGORY_ORDER}
        fetch_success_rows: list[dict[str, Any]] = []
        fetch_failure_rows: list[dict[str, Any]] = []
        processing_exception_rows: list[dict[str, Any]] = []

        run_dt = datetime.now(timezone.utc)
        rdays = recency_days_from_env()
        recency_cutoff = cutoff_date_for_run(run_dt, rdays) if rdays is not None else None
        if recency_cutoff is not None:
            logger.info(
                "[%s] Recency filter on: keep items with date >= %s (SCRAPER_RECENCY_DAYS=%d, UTC)",
                run_id,
                recency_cutoff.isoformat(),
                rdays,
            )
        else:
            logger.info("[%s] Recency filter off (SCRAPER_RECENCY_DAYS<=0 disables)", run_id)

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

            try:
                html_parts: list[tuple[str, str]] = []
                for fetch_url in fetch_urls:
                    logger.info("[%s] Fetch: %s (%s)", run_id, uni, fetch_url)
                    try:
                        html, fetch_err = fetch_html_detailed(fetch_url)
                    except Exception as fe:
                        fetch_err = f"{type(fe).__name__}: {fe}"
                        html = None
                        logger.warning("[%s] Fetch raised for %s (%s): %s", run_id, uni, fetch_url, fetch_err)
                    if html is not None:
                        fetch_success_rows.append(
                            {
                                "run_id": run_id,
                                "run_timestamp": run_ts,
                                "university": uni,
                                "url": fetch_url,
                            }
                        )
                        html_parts.append((fetch_url, html))
                    else:
                        fetch_failure_rows.append(
                            {
                                "run_id": run_id,
                                "run_timestamp": run_ts,
                                "university": uni,
                                "url": fetch_url,
                                "error": fetch_err or "unknown",
                            }
                        )
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
                            norm["scrape_index_date"] = run_ts[:10]
                            if recency_cutoff is not None and not keep_item_for_recency(
                                norm, recency_cutoff
                            ):
                                recency_dropped[cat] += 1
                                continue
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
            except Exception as e:
                msg = f"{type(e).__name__}: {e}"
                failed_n += 1
                failures.append({"university": uni or "?", "stage": "unexpected", "message": msg})
                logger.exception("[%s] Unexpected error processing %s", run_id, uni or "?")
                processing_exception_rows.append(
                    {
                        "run_id": run_id,
                        "run_timestamp": run_ts,
                        "university": uni or "?",
                        "stage": "unexpected",
                        "error": msg,
                    }
                )

        if item_json_log_enabled():
            try:
                write_scrape_item_jsonl(run_id, merged, CATEGORY_ORDER)
            except Exception as e:
                logger.exception("[%s] Failed writing scrape item JSONL: %s", run_id, e)

        try:
            write_fetch_url_audit_logs(run_id, fetch_success_rows, fetch_failure_rows)
        except Exception as e:
            logger.exception("[%s] Failed writing fetch URL audit logs: %s", run_id, e)

        try:
            write_processing_exception_logs(run_id, processing_exception_rows)
        except Exception as e:
            logger.exception("[%s] Failed writing processing exception logs: %s", run_id, e)

        fetch_audit_summary: dict[str, Any] = {
            "success_count": len(fetch_success_rows),
            "failure_count": len(fetch_failure_rows),
            "processing_exceptions_count": len(processing_exception_rows),
            "logs": {
                "success_dir": "logs/success/",
                "failure_dir": "logs/failure/",
                "success_fetch_run": f"logs/success/fetch_urls_{run_id}.jsonl",
                "success_fetch_latest": "logs/success/fetch_urls_latest.jsonl",
                "failure_fetch_run": f"logs/failure/fetch_urls_{run_id}.jsonl",
                "failure_fetch_latest": "logs/failure/fetch_urls_latest.jsonl",
                "failure_processing_run": f"logs/failure/processing_exceptions_{run_id}.jsonl",
                "failure_processing_latest": "logs/failure/processing_exceptions_latest.jsonl",
                "success_scraped_items_latest": "logs/success/scraped_items_latest.jsonl",
                "run_log_file": run_log_rel,
            },
        }

        recency_summary: dict[str, Any] = {
            "enabled": recency_cutoff is not None,
            "days": rdays,
            "cutoff_iso": recency_cutoff.isoformat() if recency_cutoff else None,
            "dropped_by_category": dict(recency_dropped),
            "total_dropped": sum(recency_dropped.values()),
        }

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
            recency=recency_summary,
            fetch_audit=fetch_audit_summary,
            run_log_file=run_log_rel,
        )
    finally:
        detach_run_log_file(run_file_handler)


def run_fixtures(config_path: Path | None = None) -> dict[str, Any]:
    setup_logging()
    ensure_directories()

    run_ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_fixtures"
    run_log_rel = _run_log_relative_path(run_id)
    run_file_handler = attach_run_log_file(run_id)

    try:
        logger.info("=== Fixture scraper run %s | run_timestamp=%s ===", run_id, run_ts)
        logger.info("[%s] Per-run log file: %s", run_id, run_log_rel)

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
                        norm["scrape_index_date"] = run_ts[:10]
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
            recency=_neutral_recency_summary(),
            fetch_audit=_neutral_fetch_audit_summary(),
            run_log_file=run_log_rel,
        )
    finally:
        detach_run_log_file(run_file_handler)


def main() -> None:
    run_once()


if __name__ == "__main__":
    main()
