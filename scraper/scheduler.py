from __future__ import annotations

import logging
import time

from main import run_once
from scheduler_config import INTERVAL_SECONDS, describe_interval
from utils.logger import setup_logging

logger = logging.getLogger("scraper.scheduler")


def main_loop() -> None:
    setup_logging()
    logger.info("Scheduler started | %s", describe_interval())
    while True:
        try:
            run_once()
        except Exception:
            logger.exception("Run failed")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main_loop()
