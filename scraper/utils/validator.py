from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Literal
from urllib.parse import urlparse

from utils.normalizer import ALLOWED_CATEGORIES

REQUIRED_FIELDS = ("university", "title", "url", "date", "category")
_DATE_ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

SkipReason = Literal["ok", "empty", "has_errors", "unknown_category"]


@dataclass
class CategoryValidationOutcome:
    valid_items: list[dict[str, Any]]
    errors: list[str] = field(default_factory=list)
    is_valid_for_copy: bool = False
    skip_reason: SkipReason = "ok"


def _semantic_checks(category: str, item: dict[str, Any], index: int) -> list[str]:
    errs: list[str] = []
    date = item.get("date")
    if not isinstance(date, str) or not _DATE_ISO_RE.match(date):
        errs.append(f"Item {index}: date must be YYYY-MM-DD, got {date!r}")
    url = item.get("url")
    if not isinstance(url, str):
        errs.append(f"Item {index}: url must be string")
    else:
        p = urlparse(url)
        if p.scheme not in ("http", "https") or not p.netloc:
            errs.append(f"Item {index}: invalid http(s) url {url!r}")
    return errs


def validate_category_bucket(category: str, items: list[dict[str, Any]]) -> CategoryValidationOutcome:
    if category not in ALLOWED_CATEGORIES:
        return CategoryValidationOutcome(
            valid_items=[],
            errors=[f"Unknown category bucket {category!r}"],
            is_valid_for_copy=False,
            skip_reason="unknown_category",
        )

    errors: list[str] = []
    valid: list[dict[str, Any]] = []

    if not items:
        return CategoryValidationOutcome(
            valid_items=[],
            errors=[],
            is_valid_for_copy=False,
            skip_reason="empty",
        )

    for i, item in enumerate(items):
        if item.get("category") != category:
            errors.append(f"Item {i}: category mismatch (expected {category}, got {item.get('category')!r})")
            continue
        missing = [f for f in REQUIRED_FIELDS if not item.get(f)]
        if missing:
            errors.append(f"Item {i}: missing fields {missing}")
            continue
        if item["category"] not in ALLOWED_CATEGORIES:
            errors.append(f"Item {i}: invalid category {item.get('category')!r}")
            continue
        sem = _semantic_checks(category, item, i)
        if sem:
            errors.extend(sem)
            continue
        valid.append(item)

    if errors:
        return CategoryValidationOutcome(
            valid_items=valid,
            errors=errors,
            is_valid_for_copy=False,
            skip_reason="has_errors",
        )

    return CategoryValidationOutcome(
        valid_items=valid,
        errors=[],
        is_valid_for_copy=len(valid) > 0,
        skip_reason="ok" if valid else "empty",
    )
