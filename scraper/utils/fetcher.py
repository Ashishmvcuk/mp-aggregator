from __future__ import annotations

import logging
import random
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

# Transient HTTP responses worth retrying (rate limit + server errors).
_RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})
# Initial attempt + retries (matches backlog: backoff + jitter on transient failures).
_MAX_ATTEMPTS = 4

_SESSION: requests.Session | None = None


def _get_session() -> requests.Session:
    global _SESSION
    if _SESSION is None:
        s = requests.Session()
        s.headers.update({"User-Agent": USER_AGENT})
        _SESSION = s
    return _SESSION


def _backoff_sleep(attempt: int) -> None:
    """Exponential backoff with small jitter (attempt is 1-based)."""
    base = 0.4 * (2 ** (attempt - 1))
    jitter = random.uniform(0, 0.35)
    time.sleep(base + jitter)


def fetch_html(url: str, timeout: int = DEFAULT_TIMEOUT) -> Optional[str]:
    """
    GET a URL and return response text. Retries on connection errors and
    retryable HTTP status codes with exponential backoff and jitter.
    """
    session = _get_session()
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            resp = session.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp.text
        except requests.HTTPError as e:
            code = e.response.status_code if e.response is not None else 0
            if attempt < _MAX_ATTEMPTS and code in _RETRYABLE_STATUS:
                logger.warning(
                    "Fetch HTTP %s for %s (attempt %d/%d), retrying after backoff",
                    code,
                    url,
                    attempt,
                    _MAX_ATTEMPTS,
                )
                _backoff_sleep(attempt)
                continue
            logger.warning("Fetch failed for %s: %s", url, e)
            return None
        except requests.RequestException as e:
            if attempt < _MAX_ATTEMPTS:
                logger.warning(
                    "Fetch error for %s (attempt %d/%d): %s — retrying after backoff",
                    url,
                    attempt,
                    _MAX_ATTEMPTS,
                    e,
                )
                _backoff_sleep(attempt)
                continue
            logger.warning("Fetch failed for %s: %s", url, e)
            return None
    return None
