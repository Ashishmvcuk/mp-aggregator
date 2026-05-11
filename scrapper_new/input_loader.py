"""Load input_data/input_10.json and build URL tasks with role hints."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from scrapper_new.categories import FIELD_TO_KIND, SOURCE_FIELD_PRIORITY
from scrapper_new.models import UrlTask

logger = logging.getLogger(__name__)

DEFAULT_INPUT_REL = Path("input_data") / "input_10.json"

_URL_FIELDS = (
    "website",
    "time_table_url",
    "results_url",
    "news_url",
    "admit_card_url",
    "student_login_url",
    "scheme_syllabus_url",
    "extra_urls",
)


def load_universities(path: Path) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("input JSON must be an array of objects")
    return data


def _dedupe_urls_by_priority(row: dict[str, Any], include_login: bool) -> dict[str, str]:
    """
    Map absolute URL string -> source_field; first seen field wins
    (``SOURCE_FIELD_PRIORITY`` order).
    """
    url_to_field: dict[str, str] = {}
    for field in SOURCE_FIELD_PRIORITY:
        if field == "student_login_url" and not include_login:
            continue
        if field not in _URL_FIELDS:
            continue
        raw = row.get(field)
        urls: list[str] = []
        if field == "extra_urls" and isinstance(raw, list):
            urls = [str(u).strip() for u in raw if str(u).strip()]
        elif isinstance(raw, str) and raw.strip():
            urls = [raw.strip()]
        for u in urls:
            if u not in url_to_field:
                url_to_field[u] = field
    return url_to_field


def build_url_tasks(rows: list[dict[str, Any]], *, include_login: bool) -> list[UrlTask]:
    tasks: list[UrlTask] = []
    for row in rows:
        name = str(row.get("name") or "").strip()
        if not name:
            logger.warning("Skipping row without name: %s", row.get("sr_no"))
            continue
        url_to_field = _dedupe_urls_by_priority(row, include_login=include_login)
        for url, field in sorted(url_to_field.items(), key=lambda x: x[0]):
            hint = FIELD_TO_KIND.get(field, "other")
            tasks.append(
                UrlTask(
                    university=name,
                    url=url,
                    source_field=field,
                    content_kind_hint=hint,
                )
            )
    return tasks
