from __future__ import annotations

import logging
import os
import random
import time
from urllib.parse import urlparse
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
_DEFAULT_INSECURE_TLS_HOSTS = frozenset(
    {
        "www.dauniv.ac.in",
        "www.amity.edu",
        "mpmsu.edu.in",
        "ralvv.mp.gov.in",
        "www.suas.ac.in",
        "rdunijbpin.mponline.gov.in",
    }
)

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


def _insecure_tls_hosts() -> set[str]:
    """
    Hosts allowed to retry once with TLS verify disabled.
    Controlled fallback for known misconfigured university cert chains.
    """
    raw = os.environ.get("SCRAPER_INSECURE_TLS_HOSTS", "").strip()
    env_hosts = {h.strip().lower() for h in raw.split(",") if h.strip()} if raw else set()
    return set(_DEFAULT_INSECURE_TLS_HOSTS) | env_hosts


def _hostname(url: str) -> str:
    try:
        return (urlparse(url).hostname or "").lower()
    except Exception:
        return ""


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
            host = _hostname(url)
            if (
                isinstance(e, requests.exceptions.SSLError)
                and host in _insecure_tls_hosts()
            ):
                try:
                    logger.warning(
                        "TLS verify failed for %s; retrying once with verify=False for host %s",
                        url,
                        host,
                    )
                    resp = session.get(url, timeout=timeout, verify=False)
                    resp.raise_for_status()
                    return resp.text
                except requests.RequestException as e2:
                    logger.warning("Fetch failed for %s after TLS fallback: %s", url, e2)
                    return None
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
