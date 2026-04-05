from __future__ import annotations

import os

DEFAULT_INTERVAL_SECONDS = 300
MIN_INTERVAL_SECONDS = 30

_env_raw = os.environ.get("SCRAPER_INTERVAL_SECONDS")
if _env_raw is None:
    INTERVAL_SECONDS = DEFAULT_INTERVAL_SECONDS
    INTERVAL_SOURCE = "default"
else:
    try:
        INTERVAL_SECONDS = int(_env_raw)
        INTERVAL_SOURCE = "SCRAPER_INTERVAL_SECONDS"
    except ValueError:
        INTERVAL_SECONDS = DEFAULT_INTERVAL_SECONDS
        INTERVAL_SOURCE = "default_invalid_env"

INTERVAL_SECONDS = max(MIN_INTERVAL_SECONDS, INTERVAL_SECONDS)


def describe_interval() -> str:
    return (
        f"interval_seconds={INTERVAL_SECONDS} "
        f"(source={INTERVAL_SOURCE}, min_clamp={MIN_INTERVAL_SECONDS})"
    )
