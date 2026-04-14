#!/usr/bin/env python3
"""
Merge portal URLs from all_mp_university_details.json into scraper/config/universities.json
as seed_urls (deduped, excluding the primary url).

Matching: normalized (host + path) of config `url` to PDF `website`; if multiple PDF rows
share the same website, match by normalized university name.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[1]
DEFAULT_DETAILS = REPO / "all_mp_university_details.json"
DEFAULT_CONFIG = REPO / "scraper" / "config" / "universities.json"

PDF_URL_KEYS = (
    "time_table_url",
    "results_url",
    "news_url",
    "admit_card_url",
    "student_login_url",
    "scheme_syllabus_url",
)


def host_key(u: str | None) -> str | None:
    if not u or not str(u).strip():
        return None
    p = urlparse(u.strip())
    net = (p.netloc or "").lower()
    if net.startswith("www."):
        net = net[4:]
    return net or None


def norm_url_key(u: str | None) -> tuple[str, str] | None:
    if not u or not str(u).strip():
        return None
    p = urlparse(u.strip())
    net = (p.netloc or "").lower()
    if net.startswith("www."):
        net = net[4:]
    path = (p.path or "").rstrip("/") or ""
    return (net, path)


def norm_name(s: str | None) -> str:
    s = re.sub(r"\s+", " ", (s or "").lower().strip())
    return s.replace(" .", ".").replace(". ", ".")


def collect_pdf_seeds(row: dict) -> list[str]:
    out: list[str] = []
    for k in PDF_URL_KEYS:
        v = row.get(k)
        if isinstance(v, str) and v.strip():
            out.append(v.strip())
    extra = row.get("extra_urls")
    if isinstance(extra, list):
        for u in extra:
            if isinstance(u, str) and u.strip():
                out.append(u.strip())
    return out


def norm_url_for_dedupe(u: str) -> str:
    return u.strip().rstrip("/")


def merge_seed_urls(primary: str, existing: list[str] | None, pdf_seeds: list[str]) -> list[str]:
    primary_n = norm_url_for_dedupe(primary)
    seen: set[str] = set()
    ordered: list[str] = []
    for u in (existing or []) + pdf_seeds:
        u = u.strip()
        if not u:
            continue
        n = norm_url_for_dedupe(u)
        if n == primary_n:
            continue
        if n in seen:
            continue
        seen.add(n)
        ordered.append(u)
    return ordered


def build_pdf_lookup(pdf_rows: list[dict]) -> dict[tuple[str, str], list[dict]]:
    by_key: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in pdf_rows:
        k = norm_url_key(r.get("website"))
        if k:
            by_key[k].append(r)
    return by_key


def pick_pdf_row(rows: list[dict], university: str) -> dict | None:
    if len(rows) == 1:
        return rows[0]
    nu = norm_name(university)
    for r in rows:
        if norm_name(r.get("name")) == nu:
            return r
    return None


def apply_pdf_to_entry(entry: dict, pdf: dict, seeds_added_counter: list[int]) -> None:
    """Merge PDF seeds into entry; set canonical `url` from PDF `website` if host matches."""
    pdf_site = (pdf.get("website") or "").strip()
    primary = str(entry.get("url", "")).strip()
    if pdf_site and host_key(pdf_site) == host_key(primary):
        if norm_url_key(pdf_site) != norm_url_key(primary):
            entry["url"] = pdf_site
            primary = pdf_site
    seeds = collect_pdf_seeds(pdf)
    before_len = len(merge_seed_urls(primary, entry.get("seed_urls"), []))
    merged = merge_seed_urls(primary, entry.get("seed_urls"), seeds)
    seeds_added_counter[0] += max(0, len(merged) - before_len)
    if merged:
        entry["seed_urls"] = merged
    else:
        entry.pop("seed_urls", None)


def run(details_path: Path, config_path: Path, dry_run: bool) -> int:
    with open(details_path, encoding="utf-8") as f:
        pdf_rows = json.load(f)
    if not isinstance(pdf_rows, list):
        raise SystemExit("details JSON must be an array")

    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)
    if not isinstance(config, list):
        raise SystemExit("config JSON must be an array")

    lookup = build_pdf_lookup(pdf_rows)
    matched = 0
    seeds_added = [0]

    # (normalized name, host) -> pdf row (for path mismatch / same host)
    by_name_host: dict[tuple[str, str], dict] = {}
    for r in pdf_rows:
        h = host_key(r.get("website"))
        n = norm_name(r.get("name"))
        if h and n:
            by_name_host[(n, h)] = r

    matched_ids: set[int] = set()

    for entry in config:
        if not isinstance(entry, dict):
            continue
        k = norm_url_key(entry.get("url"))
        if not k:
            continue
        cands = lookup.get(k)
        if not cands:
            continue
        pdf = pick_pdf_row(cands, str(entry.get("university", "")))
        if not pdf:
            continue
        matched += 1
        matched_ids.add(id(entry))
        apply_pdf_to_entry(entry, pdf, seeds_added)

    for entry in config:
        if not isinstance(entry, dict) or id(entry) in matched_ids:
            continue
        h = host_key(entry.get("url"))
        n = norm_name(entry.get("university"))
        if not h or not n:
            continue
        pdf = by_name_host.get((n, h))
        if not pdf:
            continue
        matched += 1
        apply_pdf_to_entry(entry, pdf, seeds_added)

    print(
        f"Matched {matched} config row(s) to PDF details; "
        f"net new seed URL(s) after merge: {seeds_added[0]}"
    )

    if dry_run:
        print("Dry run — not writing")
        return 0

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Wrote {config_path}")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--details", type=Path, default=DEFAULT_DETAILS)
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    raise SystemExit(run(args.details, args.config, args.dry_run))


if __name__ == "__main__":
    main()
