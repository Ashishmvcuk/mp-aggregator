from __future__ import annotations

import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SCRAPER_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = SCRAPER_ROOT.parent
OUTPUT_DIR = SCRAPER_ROOT / "output"
OUTPUT_CSV_DIR = OUTPUT_DIR / "csv"
HISTORY_DIR = OUTPUT_DIR / "history"
WEBSITE_DATA_DIR = REPO_ROOT / "website" / "public" / "data"


def ensure_directories() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_CSV_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    WEBSITE_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _atomic_write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def write_json(path: Path, payload: Any, indent: int = 2) -> None:
    text = json.dumps(payload, indent=indent, ensure_ascii=False) + "\n"
    _atomic_write(path, text)


def safe_write_json(path: Path, payload: Any, indent: int = 2) -> None:
    """
    Serialize, validate JSON in memory, write temp file, read-back parse, then replace.
    Used for website/public/data to avoid replacing a good file with corrupt JSON.
    """
    text = json.dumps(payload, indent=indent, ensure_ascii=False) + "\n"
    json.loads(text)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        with open(tmp, encoding="utf-8") as rf:
            json.loads(rf.read())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def adapt_results_for_website(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Map canonical `url` to `result_url` for the React app."""
    out = []
    for it in items:
        out.append(
            {
                "university": it["university"],
                "title": it["title"],
                "result_url": it["url"],
                "date": it["date"],
            }
        )
    return out


def count_json_list_items(path: Path) -> int | None:
    if not path.is_file():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return len(data)
    except (json.JSONDecodeError, OSError):
        return None
    return None


def write_category_output(category: str, items: list[dict[str, Any]]) -> Path:
    path = OUTPUT_DIR / f"{category}.json"
    write_json(path, items)
    return path


def write_history_snapshot(category: str, items: list[dict[str, Any]]) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = HISTORY_DIR / f"{ts}_{category}.json"
    write_json(path, items)


def sync_category_to_website(category: str, items: list[dict[str, Any]]) -> Path:
    dest = WEBSITE_DATA_DIR / f"{category}.json"
    prev_count = count_json_list_items(dest)
    prev_size = dest.stat().st_size if dest.is_file() else None

    if category == "results":
        payload = adapt_results_for_website(items)
    else:
        payload = items

    safe_write_json(dest, payload)
    new_count = len(payload)
    if prev_count is not None:
        logger.info(
            "Website %s: replaced list len %s -> %s (was %s bytes)",
            dest.name,
            prev_count,
            new_count,
            prev_size,
        )
    else:
        logger.info("Website %s: wrote %d items (new file)", dest.name, new_count)
    return dest


def write_run_summary(summary: dict[str, Any]) -> Path:
    path = OUTPUT_DIR / "run_summary.json"
    write_json(path, summary)
    return path


def read_scraper_version_file() -> str:
    p = SCRAPER_ROOT / "VERSION"
    if p.is_file():
        return p.read_text(encoding="utf-8").strip()
    return "0.0.0"


def read_site_package_version() -> str:
    pkg = REPO_ROOT / "website" / "package.json"
    if not pkg.is_file():
        return "0.0.0"
    try:
        with open(pkg, encoding="utf-8") as f:
            data = json.load(f)
        v = data.get("version")
        return str(v).strip() if v is not None else "0.0.0"
    except (json.JSONDecodeError, OSError, TypeError):
        return "0.0.0"


def write_scrape_meta(summary: dict[str, Any]) -> Path:
    """Last-run metadata for the website UI (synced to public/data/scrape_meta.json)."""
    payload: dict[str, Any] = {
        "scrapedAt": summary["run_timestamp"],
        "runId": summary["run_id"],
        "scraperVersion": read_scraper_version_file(),
        "siteReleaseVersion": read_site_package_version(),
        "universitiesSuccess": summary["universities_success"],
        "universitiesFailed": summary["universities_failed"],
        "categoryCounts": summary.get("unique_counts", {}),
    }
    ci = os.environ.get("SCRAPER_CI_RUN_ID", "").strip()
    if ci:
        payload["ciRunId"] = ci
    path = OUTPUT_DIR / "scrape_meta.json"
    write_json(path, payload)
    return path


def website_relative_data_path(category: str) -> str:
    return f"public/data/{category}.json"
