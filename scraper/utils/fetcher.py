from __future__ import annotations

import logging
import os
import random
import threading
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
_DEFAULT_MAX_ATTEMPTS = 3


def _resolved_timeout(explicit: Optional[int]) -> int:
    """Per-request override, else SCRAPER_FETCH_TIMEOUT (seconds), clamped 5–120."""
    if explicit is not None:
        return max(5, min(int(explicit), 120))
    raw = os.environ.get("SCRAPER_FETCH_TIMEOUT", "").strip()
    if not raw:
        return DEFAULT_TIMEOUT
    try:
        return max(5, min(int(raw), 120))
    except ValueError:
        return DEFAULT_TIMEOUT


def _fast_fail_unreachable() -> bool:
    """
    When true, do not retry ConnectTimeout / ConnectionError (dead DNS, refused, hung TLS).
    Saves ~2× connect wait on CI runners where many university hosts never respond.
    """
    return os.environ.get("SCRAPER_FETCH_FAST_FAIL_CONNECT", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _max_fetch_attempts() -> int:
    """Upper bound on GET attempts per URL (no infinite retries). Default 3; override via SCRAPER_FETCH_MAX_ATTEMPTS."""
    raw = os.environ.get("SCRAPER_FETCH_MAX_ATTEMPTS", str(_DEFAULT_MAX_ATTEMPTS)).strip()
    try:
        n = int(raw)
    except ValueError:
        n = _DEFAULT_MAX_ATTEMPTS
    return max(1, min(n, 10))


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

_tls = threading.local()


def _get_session() -> requests.Session:
    """Thread-local Session — safe for SCRAPER_FETCH_WORKERS > 1 (requests.Session is not thread-safe)."""
    sess: requests.Session | None = getattr(_tls, "session", None)
    if sess is None:
        sess = requests.Session()
        sess.headers.update({"User-Agent": USER_AGENT})
        _tls.session = sess
    return sess


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


def fetch_html_detailed(
    url: str, timeout: Optional[int] = None
) -> tuple[Optional[str], Optional[str]]:
    """
    GET a URL and return (response text, None) on success, or (None, error_summary).
    Retries transient failures up to SCRAPER_FETCH_MAX_ATTEMPTS (default 3), then stops.
    Timeout: optional per-call seconds, else SCRAPER_FETCH_TIMEOUT env (default 30).
    """
    session = _get_session()
    max_attempts = _max_fetch_attempts()
    last_err: Optional[str] = None
    tmo = _resolved_timeout(timeout)

    for attempt in range(1, max_attempts + 1):
        try:
            resp = session.get(url, timeout=tmo)
            resp.raise_for_status()
            return resp.text, None
        except requests.HTTPError as e:
            code = e.response.status_code if e.response is not None else 0
            last_err = f"HTTP {code}"
            if attempt < max_attempts and code in _RETRYABLE_STATUS:
                logger.warning(
                    "Fetch HTTP %s for %s (attempt %d/%d), retrying after backoff",
                    code,
                    url,
                    attempt,
                    max_attempts,
                )
                _backoff_sleep(attempt)
                continue
            logger.warning("Fetch failed for %s: %s", url, e)
            return None, last_err
        except requests.RequestException as e:
            host = _hostname(url)
            if isinstance(e, requests.exceptions.SSLError) and host in _insecure_tls_hosts():
                try:
                    logger.warning(
                        "TLS verify failed for %s; retrying once with verify=False for host %s",
                        url,
                        host,
                    )
                    resp = session.get(url, timeout=tmo, verify=False)
                    resp.raise_for_status()
                    return resp.text, None
                except requests.RequestException as e2:
                    msg = f"TLS fallback failed: {type(e2).__name__}: {e2}"
                    logger.warning("Fetch failed for %s after TLS fallback: %s", url, e2)
                    return None, msg
            last_err = f"{type(e).__name__}: {e}"
            if _fast_fail_unreachable() and isinstance(
                e,
                (
                    requests.exceptions.ConnectTimeout,
                    requests.exceptions.ConnectionError,
                ),
            ):
                logger.warning(
                    "Fetch failed for %s (fast-fail connect, no retry): %s",
                    url,
                    e,
                )
                return None, last_err
            if attempt < max_attempts:
                logger.warning(
                    "Fetch error for %s (attempt %d/%d): %s — retrying after backoff",
                    url,
                    attempt,
                    max_attempts,
                    e,
                )
                _backoff_sleep(attempt)
                continue
            logger.warning("Fetch failed for %s: %s", url, e)
            return None, last_err
    return None, last_err or "fetch failed"


def fetch_html(url: str, timeout: Optional[int] = None) -> Optional[str]:
    """
    GET a URL and return response text. Same retry policy as fetch_html_detailed.
    """
    body, _ = fetch_html_detailed(url, timeout=timeout)
    return body
