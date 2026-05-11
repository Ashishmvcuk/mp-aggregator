"""Orchestrate fetch → extract → normalize → filter → dedupe → write."""

from __future__ import annotations

import json
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Literal

from scrapper_new.categories import kind_to_website_category
from scrapper_new.dates import parse_http_date_header
from scrapper_new.extract import extract_from_html
from scrapper_new.fetch import fetch_url
from scrapper_new.input_loader import build_url_tasks, load_universities
from scrapper_new.models import (
    NormalizedItem,
    RawExtracted,
    RunCounters,
    UniversityStats,
    UrlTask,
    WEBSITE_CATEGORIES,
)

logger = logging.getLogger(__name__)

_MAX_LINKS_PER_PAGE = 150
SkipReason = Literal["old", "no_signal"]


def _norm_title_key(title: str) -> str:
    t = (title or "").lower().strip()
    t = re.sub(r"\s+", " ", t)
    return t


def _dedupe_key(title: str, url: str) -> str:
    return f"{_norm_title_key(title)}|{(url or '').strip()}"


def _recency_days() -> int:
    raw = os.environ.get("SCRAPPER_NEW_RECENCY_DAYS", "60").strip()
    try:
        n = int(raw)
        return max(1, min(n, 365))
    except ValueError:
        return 60


def _workers() -> int:
    raw = os.environ.get("SCRAPPER_NEW_WORKERS", "6").strip()
    try:
        return max(1, min(int(raw), 32))
    except ValueError:
        return 6


def _recent_year_signal(title: str, today: date) -> bool:
    ys = [int(y) for y in re.findall(r"\b(20\d{2})\b", title)]
    if not ys:
        return False
    y0 = today.year
    return any(y0 - 1 <= y <= y0 + 1 for y in ys)


def normalize_row(
    raw: RawExtracted,
    *,
    source_page_url: str,
    page_last_modified: date | None,
    cutoff: date,
    scraped_at_iso: str,
    today_utc: date,
) -> tuple[NormalizedItem | None, SkipReason | None]:
    """Return (item, None) on success, (None, reason) when filtered out."""
    published: str | None = raw.published_date_iso
    pub_date: date | None = None
    if published:
        try:
            pub_date = date.fromisoformat(published[:10])
        except ValueError:
            pub_date = None

    effective_date: date | None = None
    date_confidence: str

    if pub_date is not None:
        if pub_date < cutoff:
            return None, "old"
        effective_date = pub_date
        date_confidence = "high"
    elif page_last_modified is not None and page_last_modified >= cutoff:
        effective_date = page_last_modified
        date_confidence = "medium"
    elif _recent_year_signal(raw.title, today_utc):
        effective_date = today_utc
        date_confidence = "low"
    else:
        return None, "no_signal"

    assert effective_date is not None
    date_iso = effective_date.isoformat()
    cat = kind_to_website_category(raw.content_kind)
    if cat not in WEBSITE_CATEGORIES:
        cat = "news"

    return (
        NormalizedItem(
            university=raw.university,
            title=raw.title.strip()[:500],
            description=(raw.description or "")[:2000],
            content_kind=raw.content_kind,
            category=cat,
            url=raw.url.strip(),
            date=date_iso,
            published_date_raw=raw.published_date_raw,
            date_confidence=date_confidence,  # type: ignore[arg-type]
            scraped_at=scraped_at_iso,
            source_page_url=source_page_url,
        ),
        None,
    )


def run_pipeline(
    *,
    input_path: Path,
    output_dir: Path,
    emit_website_buckets: bool,
    include_login: bool,
) -> dict[str, Any]:
    run_started = datetime.now(timezone.utc).replace(microsecond=0)
    run_started_iso = run_started.isoformat()
    run_id = f"scrapper_new_{run_started.strftime('%Y%m%dT%H%M%SZ')}"

    output_dir.mkdir(parents=True, exist_ok=True)
    rows = load_universities(input_path)
    tasks = build_url_tasks(rows, include_login=include_login)
    logger.info("Built %d fetch tasks from %s", len(tasks), input_path)

    recency_days = _recency_days()
    now = datetime.now(timezone.utc)
    today_utc = now.date()
    cutoff = today_utc - timedelta(days=recency_days)
    scraped_at_iso = now.replace(microsecond=0).isoformat()

    uni_stats: dict[str, UniversityStats] = {}
    for row in rows:
        n = str(row.get("name") or "").strip()
        if n:
            uni_stats[n] = UniversityStats(name=n)

    counters = RunCounters()
    all_normalized: list[NormalizedItem] = []

    workers = _workers()

    def _one(task: UrlTask) -> tuple[UrlTask, Any]:
        fr = fetch_url(task.url)
        return task, fr

    results: list[tuple[UrlTask, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(_one, t): t for t in tasks}
        for fut in as_completed(futs):
            task = futs[fut]
            try:
                results.append(fut.result())
            except Exception as e:  # noqa: BLE001
                logger.exception("worker_failed url=%s: %s", task.url, e)
                counters.fetch_failed += 1
                st = uni_stats.get(task.university)
                if st:
                    st.fetch_failed += 1

    for task, fr in results:
        st = uni_stats.get(task.university)
        if not fr.ok:
            counters.fetch_failed += 1
            if st:
                st.fetch_failed += 1
            logger.info(
                "skipped_fetch university=%s url=%s error=%s",
                task.university,
                task.url,
                fr.error or fr.status_code,
            )
            continue
        counters.fetch_ok += 1
        if st:
            st.fetch_ok += 1

        html = fr.html or ""
        page_lm = parse_http_date_header(fr.last_modified)
        raw_items = extract_from_html(
            html,
            source_page_url=task.url,
            university=task.university,
            content_kind_hint=task.content_kind_hint,
        )
        raw_items = raw_items[:_MAX_LINKS_PER_PAGE]
        if st:
            st.items_extracted += len(raw_items)
        counters.items_extracted += len(raw_items)

        for raw in raw_items:
            norm, skip = normalize_row(
                raw,
                source_page_url=task.url,
                page_last_modified=page_lm,
                cutoff=cutoff,
                scraped_at_iso=scraped_at_iso,
                today_utc=today_utc,
            )
            if norm is None:
                if skip == "old":
                    counters.skipped_old += 1
                else:
                    counters.skipped_no_signal += 1
                continue
            all_normalized.append(norm)

    seen: set[str] = set()
    deduped: list[NormalizedItem] = []
    for it in all_normalized:
        k = _dedupe_key(it.title, it.url)
        if k in seen:
            counters.skipped_duplicate += 1
            continue
        seen.add(k)
        deduped.append(it)

    for it in deduped:
        st = uni_stats.get(it.university)
        if st:
            st.items_emitted += 1

    counters.items_out = len(deduped)

    out_json = output_dir / "input10_updates.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump([x.to_json_dict() for x in deduped], f, indent=2, ensure_ascii=False)

    run_completed = datetime.now(timezone.utc).replace(microsecond=0)
    summary = {
        "run_id": run_id,
        "run_started_at": run_started_iso,
        "run_completed_at": run_completed.isoformat(),
        "input_path": str(input_path),
        "recency_days": recency_days,
        "cutoff_iso": cutoff.isoformat(),
        "scraped_at_reference": scraped_at_iso,
        "fetch_workers": workers,
        "totals": {
            "fetch_ok": counters.fetch_ok,
            "fetch_failed": counters.fetch_failed,
            "items_extracted": counters.items_extracted,
            "items_passing_recency_pre_dedupe": len(all_normalized),
            "skipped_old": counters.skipped_old,
            "skipped_no_signal": counters.skipped_no_signal,
            "skipped_duplicate": counters.skipped_duplicate,
            "items_out": counters.items_out,
        },
        "universities": [
            {
                "name": s.name,
                "fetch_ok": s.fetch_ok,
                "fetch_failed": s.fetch_failed,
                "items_extracted": s.items_extracted,
                "items_emitted": s.items_emitted,
            }
            for s in sorted(uni_stats.values(), key=lambda x: x.name)
        ],
    }
    with open(output_dir / "run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    if emit_website_buckets:
        buckets: dict[str, list[dict[str, Any]]] = {c: [] for c in WEBSITE_CATEGORIES}
        for it in deduped:
            buckets.setdefault(it.category, []).append(it.to_website_dict())
        wb = output_dir / "website_buckets"
        wb.mkdir(parents=True, exist_ok=True)
        for cat in WEBSITE_CATEGORIES:
            path = wb / f"{cat}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(buckets.get(cat, []), f, indent=2, ensure_ascii=False)
        logger.info("Wrote website bucket files under %s", wb)

    logger.info(
        "done items_out=%s skipped_old=%s skipped_no_signal=%s skipped_dup=%s fetch_fail=%s",
        counters.items_out,
        counters.skipped_old,
        counters.skipped_no_signal,
        counters.skipped_duplicate,
        counters.fetch_failed,
    )
    return summary
