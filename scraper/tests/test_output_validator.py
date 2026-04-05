from __future__ import annotations

import json
from pathlib import Path


from utils.normalizer import CATEGORY_ORDER
from utils.output_validator import validate_output_directory


def test_validate_empty_outputs(tmp_path: Path) -> None:
    """Empty category arrays are structurally valid."""
    for cat in CATEGORY_ORDER:
        (tmp_path / f"{cat}.json").write_text(json.dumps([]) + "\n", encoding="utf-8")
    (tmp_path / "run_summary.json").write_text(
        json.dumps({"universities_success": 0, "all_categories_empty": True}),
        encoding="utf-8",
    )
    r = validate_output_directory(tmp_path, strict_run=False)
    assert all(cr.valid for cr in r.categories.values())


def test_validate_detects_duplicate_url_in_results(tmp_path: Path) -> None:
    dup = [
        {
            "university": "U",
            "title": "A",
            "url": "https://example.com/same",
            "date": "2026-01-01",
            "category": "results",
        },
        {
            "university": "U",
            "title": "B",
            "url": "https://example.com/same",
            "date": "2026-01-02",
            "category": "results",
        },
    ]
    for cat in CATEGORY_ORDER:
        data = dup if cat == "results" else []
        (tmp_path / f"{cat}.json").write_text(json.dumps(data), encoding="utf-8")
    r = validate_output_directory(tmp_path, strict_run=False)
    assert not r.categories["results"].valid
    assert r.categories["results"].duplicate_rows_removed == 1


def test_strict_run_fails_on_empty_after_success(tmp_path: Path) -> None:
    for cat in CATEGORY_ORDER:
        (tmp_path / f"{cat}.json").write_text(json.dumps([]) + "\n", encoding="utf-8")
    (tmp_path / "run_summary.json").write_text(
        json.dumps({"universities_success": 1, "all_categories_empty": True}),
        encoding="utf-8",
    )
    r = validate_output_directory(tmp_path, strict_run=True)
    assert not r.ok
