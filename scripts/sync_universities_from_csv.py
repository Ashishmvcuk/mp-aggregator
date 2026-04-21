#!/usr/bin/env python3
"""Rebuild scraper config (and intermediate JSON) from ALL MP UNIVERSITY DETAILS.csv.

The CSV is the canonical source of university URLs. Running this script will:

1. Parse the CSV and write a cleaned intermediate representation to
   ``all_mp_university_details.json``.
2. Regenerate ``scraper/config/universities.json`` from scratch, using the
   ``WEBSITES`` column as each entry's primary ``url`` and the remaining URL
   columns (TIME TABLE, RESULTS, NEWS & NOTIFICATIONS, ADMIT CARD, STUDENT
   LOGIN, Scheme/Syllabus) as deduped ``seed_urls``.

Special parser overrides (davv, rgpv) are preserved based on university name.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[1]
DEFAULT_CSV = REPO / "ALL MP UNIVERSITY DETAILS.csv"
DEFAULT_DETAILS = REPO / "all_mp_university_details.json"
DEFAULT_CONFIG = REPO / "scraper" / "config" / "universities.json"

CSV_URL_COLUMNS = (
    ("time_table_url", "TIME TABLE"),
    ("results_url", "RESULTS"),
    ("news_url", "NEWS & NOTIFICATIONS"),
    ("admit_card_url", "ADMIT CARD"),
    ("student_login_url", "STUDENT LOGIN"),
    ("scheme_syllabus_url", "Scheme/Syllabus"),
)

# Some CSV rows have a blank ``Name of the University`` cell. Map the primary
# website to a known canonical name so we still emit a usable entry.
NAME_FALLBACKS_BY_WEBSITE: dict[str, str] = {
    "https://lnctu.ac.in/": "LNCT University",
}


def _norm_name(s: str | None) -> str:
    return re.sub(r"\s+", " ", (s or "").lower().strip())


def _parsers_for(name: str) -> list[str] | None:
    """Return a ``parsers`` override for universities that need extra parsers.

    ``None`` means "use the default single mp_portal parser".
    """
    n = _norm_name(name)
    if "devi ahilya" in n:
        return ["mp_portal", "davv"]
    if "rajiv gandhi prodoyogiki" in n:
        return ["mp_portal", "rgpv"]
    return None


def _clean_url(u: str | None) -> str:
    if not u:
        return ""
    u = u.strip()
    return u if u.lower().startswith(("http://", "https://")) else ""


def _dedupe_seeds(primary: str, seeds: list[str]) -> list[str]:
    primary_n = primary.strip().rstrip("/")
    seen: set[str] = set()
    out: list[str] = []
    for u in seeds:
        u = u.strip()
        if not u:
            continue
        key = u.rstrip("/")
        if key == primary_n or key in seen:
            continue
        seen.add(key)
        out.append(u)
    return out


def _is_university_row(row: dict[str, str]) -> bool:
    sr_no = (row.get("Sr.No") or "").strip()
    if not sr_no.isdigit():
        return False
    type_ = (row.get("Type") or "").strip()
    if not type_:
        return False
    return bool(_clean_url(row.get("WEBSITES")))


def parse_csv(csv_path: Path) -> list[dict[str, Any]]:
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        all_rows = [r for r in reader if any((c or "").strip() for c in r)]

    header_idx = next(
        (i for i, r in enumerate(all_rows) if r and r[0].strip() == "Sr.No"),
        None,
    )
    if header_idx is None:
        raise SystemExit("CSV header row ('Sr.No,Type,...') not found")
    header = [c.strip() for c in all_rows[header_idx]]
    rows: list[dict[str, str]] = []
    for raw in all_rows[header_idx + 1 :]:
        if raw and raw[0].strip() == "Sr.No":
            continue
        padded = list(raw) + [""] * (len(header) - len(raw))
        rows.append(dict(zip(header, padded)))

    details: list[dict[str, Any]] = []
    for r in rows:
        if not _is_university_row(r):
            continue
        website = _clean_url(r.get("WEBSITES"))
        name = (r.get("Name of the University") or "").strip()
        if not name:
            name = NAME_FALLBACKS_BY_WEBSITE.get(website, "")
        if not name:
            continue
        entry: dict[str, Any] = {
            "sr_no": int(r["Sr.No"].strip()),
            "type": (r.get("Type") or "").strip(),
            "name": name,
            "website": website,
        }
        for key, col in CSV_URL_COLUMNS:
            entry[key] = _clean_url(r.get(col))
        entry["extra_urls"] = []
        entry["address"] = (r.get("Address") or "").strip()
        entry["zip"] = (r.get("Zip") or "").strip()
        entry["state"] = (r.get("state") or "").strip()
        entry["status"] = (r.get("Status") or "").strip()
        details.append(entry)
    return details


def build_config(details: list[dict[str, Any]]) -> list[dict[str, Any]]:
    config: list[dict[str, Any]] = []
    for d in details:
        primary = d["website"]
        seeds_raw = [d[k] for k, _ in CSV_URL_COLUMNS] + list(d.get("extra_urls") or [])
        seeds = _dedupe_seeds(primary, [s for s in seeds_raw if s])

        entry: dict[str, Any] = {
            "university": d["name"],
            "url": primary,
            "enabled": True,
            "type": d.get("type", ""),
        }
        parsers = _parsers_for(d["name"])
        if parsers:
            entry["parsers"] = parsers
        else:
            entry["parser"] = "mp_portal"
        if seeds:
            entry["seed_urls"] = seeds
        config.append(entry)
    return config


def _validate_http_urls(config: list[dict[str, Any]]) -> list[str]:
    """Return a list of human-readable issues found in the generated config."""
    issues: list[str] = []
    for e in config:
        uni = e.get("university", "?")
        for key in ("url", *(f"seed_urls[{i}]" for i in range(len(e.get("seed_urls") or [])))):
            if key == "url":
                u = e.get("url")
            else:
                idx = int(key[key.index("[") + 1 : key.index("]")])
                u = e["seed_urls"][idx]
            if not u:
                issues.append(f"{uni}: empty {key}")
                continue
            p = urlparse(u)
            if p.scheme not in ("http", "https") or not p.netloc:
                issues.append(f"{uni}: malformed {key}={u!r}")
    return issues


def run(csv_path: Path, details_path: Path, config_path: Path, dry_run: bool) -> int:
    if not csv_path.is_file():
        raise SystemExit(f"CSV not found: {csv_path}")

    details = parse_csv(csv_path)
    if not details:
        raise SystemExit("No university rows parsed from CSV")

    config = build_config(details)
    issues = _validate_http_urls(config)
    if issues:
        print(f"Found {len(issues)} URL issue(s):")
        for line in issues[:20]:
            print(f"  - {line}")
        if len(issues) > 20:
            print(f"  ... {len(issues) - 20} more")

    print(f"Parsed {len(details)} universities from {csv_path.name}")
    total_seeds = sum(len(e.get("seed_urls") or []) for e in config)
    print(f"Generated config: {len(config)} entries, {total_seeds} total seed URL(s)")

    if dry_run:
        print("Dry run — not writing")
        return 0

    with open(details_path, "w", encoding="utf-8") as f:
        json.dump(details, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Wrote {details_path}")

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Wrote {config_path}")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    ap.add_argument("--details", type=Path, default=DEFAULT_DETAILS)
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    raise SystemExit(run(args.csv, args.details, args.config, args.dry_run))


if __name__ == "__main__":
    main()
