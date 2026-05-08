"""Tests for announcement-date recency filtering."""
from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from utils.recency import (
    cutoff_date_for_run,
    item_json_log_enabled,
    keep_item_for_recency,
    parse_item_announcement_date,
    recency_days_from_env,
)


def test_keep_item_on_cutoff_day() -> None:
    cutoff = date(2026, 3, 1)
    assert keep_item_for_recency({"date": "2026-03-01"}, cutoff) is True


def test_drop_item_before_cutoff() -> None:
    cutoff = date(2026, 3, 1)
    assert keep_item_for_recency({"date": "2026-02-28"}, cutoff) is False


def test_drop_missing_date() -> None:
    assert keep_item_for_recency({"date": None}, date(2020, 1, 1)) is False
    assert keep_item_for_recency({}, date(2020, 1, 1)) is False


def test_parse_item_date_trims_time_suffix() -> None:
    assert parse_item_announcement_date({"date": "2026-04-01 10:00:00"}) == date(2026, 4, 1)


def test_parse_item_date_invalid() -> None:
    assert parse_item_announcement_date({"date": "not-a-date"}) is None


def test_cutoff_date_for_run_subtracts_days() -> None:
    ref = datetime(2026, 5, 8, 12, 0, 0, tzinfo=timezone.utc)
    assert cutoff_date_for_run(ref, 60) == date(2026, 3, 9)


def test_recency_days_from_env_zero_disables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SCRAPER_RECENCY_DAYS", "0")
    assert recency_days_from_env() is None


def test_recency_days_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SCRAPER_RECENCY_DAYS", raising=False)
    assert recency_days_from_env() == 60


def test_recency_days_negative_disables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SCRAPER_RECENCY_DAYS", "-1")
    assert recency_days_from_env() is None


def test_recency_days_invalid_falls_back_to_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SCRAPER_RECENCY_DAYS", "bogus")
    assert recency_days_from_env() == 60


def test_item_json_log_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SCRAPER_ITEM_LOG", raising=False)
    assert item_json_log_enabled() is False


def test_item_json_log_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SCRAPER_ITEM_LOG", "1")
    assert item_json_log_enabled() is True
