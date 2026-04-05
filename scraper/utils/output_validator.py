from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from utils.dedupe import dedupe_category
from utils.normalizer import CATEGORY_ORDER
from utils.validator import validate_category_bucket


@dataclass
class CategoryFileReport:
    category: str
    path: Path
    item_count: int
    valid: bool
    errors: list[str] = field(default_factory=list)
    duplicate_rows_removed: int = 0


@dataclass
class OutputDirectoryReport:
    ok: bool
    categories: dict[str, CategoryFileReport] = field(default_factory=dict)
    global_errors: list[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.global_errors.append(msg)
        self.ok = False


def _load_category_json(path: Path) -> tuple[list[Any] | None, str | None]:
    if not path.is_file():
        return None, f"Missing file: {path}"
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON in {path}: {e}"
    if not isinstance(data, list):
        return None, f"{path} must contain a JSON array"
    return data, None


def validate_output_directory(
    output_dir: Path,
    *,
    strict_run: bool = False,
) -> OutputDirectoryReport:
    report = OutputDirectoryReport(ok=True, categories={})

    summary_path = output_dir / "run_summary.json"
    if strict_run and summary_path.is_file():
        try:
            with open(summary_path, encoding="utf-8") as f:
                summary = json.load(f)
            if summary.get("universities_success", 0) >= 1 and summary.get("all_categories_empty"):
                report.add_error(
                    "run_summary.json: universities_success >= 1 but all_categories_empty is true"
                )
        except (json.JSONDecodeError, OSError) as e:
            report.add_error(f"Could not read run_summary.json for --strict-run: {e}")

    for cat in CATEGORY_ORDER:
        path = output_dir / f"{cat}.json"
        items, err = _load_category_json(path)
        cr = CategoryFileReport(category=cat, path=path, item_count=0, valid=False, errors=[])
        report.categories[cat] = cr
        if err:
            cr.errors.append(err)
            report.add_error(f"{cat}: {err}")
            continue
        assert items is not None
        cr.item_count = len(items)

        outcome = validate_category_bucket(cat, items)
        if outcome.errors:
            cr.errors.extend(outcome.errors)
            for e in outcome.errors[:10]:
                report.add_error(f"{cat}: {e}")
            if len(outcome.errors) > 10:
                report.add_error(f"{cat}: ... and {len(outcome.errors) - 10} more errors")

        _, removed = dedupe_category(cat, items)
        cr.duplicate_rows_removed = removed
        if removed > 0:
            msg = f"{cat}: found {removed} duplicate row(s) by dedupe key (output should be pre-deduped)"
            cr.errors.append(msg)
            report.add_error(msg)

        if not outcome.errors and removed == 0:
            cr.valid = True
        else:
            cr.valid = False

    return report
