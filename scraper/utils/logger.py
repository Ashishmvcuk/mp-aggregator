from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
RUNS_LOG_DIR = LOG_DIR / "runs"
LOG_FILE = LOG_DIR / "scraper.log"
MAX_BYTES = 2_000_000
BACKUP_COUNT = 5

_configured = False


def attach_run_log_file(run_id: str) -> logging.Handler:
    """
    One log file per scraper run: logs/runs/scraper_<run_id>.log
    (run_id is UTC date+time, e.g. 20260508T143022Z). Remove with detach_run_log_file in a finally block.
    """
    RUNS_LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = RUNS_LOG_DIR / f"scraper_{run_id}.log"
    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    fh = logging.FileHandler(path, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    logging.getLogger().addHandler(fh)
    return fh


def detach_run_log_file(handler: Optional[logging.Handler]) -> None:
    if handler is None:
        return
    root = logging.getLogger()
    if handler in root.handlers:
        root.removeHandler(handler)
    handler.flush()
    handler.close()


def setup_logging() -> None:
    global _configured
    if _configured:
        return
    _configured = True
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    for h in list(root.handlers):
        root.removeHandler(h)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)
    root.addHandler(sh)
    fh = RotatingFileHandler(LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT)
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    root.addHandler(fh)
