"""HTTP fetch with retries, timeouts, and thread-local sessions."""

from __future__ import annotations

import logging
import os
import random
import threading
import time
from typing import Optional
from urllib.parse import urlparse

import requests

from scrapper_new.models import FetchResult

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
_RETRYABLE = frozenset({429, 500, 502, 503, 504})

_tls = threading.local()


def _session() -> requests.Session:
    sess: requests.Session | None = getattr(_tls, "session", None)
    if sess is None:
        sess = requests.Session()
        sess.headers.update({"User-Agent": USER_AGENT})
        _tls.session = sess
    return sess


def _timeout() -> int:
    raw = os.environ.get("SCRAPPER_NEW_TIMEOUT", "").strip() or os.environ.get(
        "SCRAPER_FETCH_TIMEOUT", ""
    ).strip()
    if not raw:
        return 30
    try:
        return max(5, min(int(raw), 120))
    except ValueError:
        return 30


def _max_attempts() -> int:
    raw = os.environ.get("SCRAPPER_NEW_MAX_ATTEMPTS", "").strip() or os.environ.get(
        "SCRAPER_FETCH_MAX_ATTEMPTS", "3"
    ).strip()
    try:
        return max(1, min(int(raw), 10))
    except ValueError:
        return 3


def _fast_fail_connect() -> bool:
    return os.environ.get("SCRAPPER_NEW_FAST_FAIL_CONNECT", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ) or os.environ.get("SCRAPER_FETCH_FAST_FAIL_CONNECT", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _backoff(attempt: int) -> None:
    base = 0.35 * (2 ** (attempt - 1))
    time.sleep(base + random.uniform(0, 0.25))


def fetch_url(url: str) -> FetchResult:
    """GET one URL; never raises — errors are in FetchResult."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return FetchResult(url=url, ok=False, error="invalid_url")

    timeout = _timeout()
    attempts = _max_attempts()
    sess = _session()
    last_err: str | None = None

    for attempt in range(1, attempts + 1):
        try:
            r = sess.get(url, timeout=timeout, allow_redirects=True)
            ct = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            lm = r.headers.get("Last-Modified")
            if r.status_code in _RETRYABLE and attempt < attempts:
                logger.debug("Retry %s %s (%s)", attempt, url, r.status_code)
                _backoff(attempt)
                continue
            if r.status_code != 200:
                return FetchResult(
                    url=url,
                    ok=False,
                    status_code=r.status_code,
                    error=f"http_{r.status_code}",
                    last_modified=lm,
                )
            if "html" not in ct and "text" not in ct and ct not in ("application/octet-stream", ""):
                return FetchResult(
                    url=url,
                    ok=False,
                    status_code=r.status_code,
                    content_type=ct,
                    error=f"non_html_content_type:{ct or 'empty'}",
                    last_modified=lm,
                )
            text = r.text or ""
            if not text.strip():
                return FetchResult(
                    url=url,
                    ok=True,
                    status_code=r.status_code,
                    html="",
                    content_type=ct,
                    last_modified=lm,
                )
            return FetchResult(
                url=url,
                ok=True,
                status_code=r.status_code,
                html=text,
                content_type=ct,
                last_modified=lm,
            )
        except requests.Timeout as e:
            last_err = f"timeout:{e}"
            if _fast_fail_connect() and attempt >= attempts:
                break
        except requests.ConnectionError as e:
            last_err = f"connection:{e}"
            if _fast_fail_connect():
                break
        except requests.RequestException as e:
            last_err = f"request:{e}"
        if attempt < attempts:
            _backoff(attempt)

    logger.info("fetch_failed url=%s error=%s", url, last_err)
    return FetchResult(url=url, ok=False, error=last_err or "unknown")
