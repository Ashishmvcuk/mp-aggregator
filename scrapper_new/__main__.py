"""Allow ``python -m scrapper_new`` from repository root (PYTHONPATH includes cwd)."""

from __future__ import annotations

import sys

from scrapper_new.run import main

if __name__ == "__main__":
    raise SystemExit(main())
