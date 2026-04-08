from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from utils.fetcher import fetch_html


@pytest.fixture
def mock_session():
    with patch("utils.fetcher._get_session") as m:
        yield m


def test_fetch_html_success_first_try(mock_session):
    sess = MagicMock()
    resp = MagicMock()
    resp.text = "<html>ok</html>"
    resp.raise_for_status = MagicMock()
    sess.get.return_value = resp
    mock_session.return_value = sess

    assert fetch_html("https://example.edu/") == "<html>ok</html>"
    sess.get.assert_called_once_with("https://example.edu/", timeout=30)


def test_fetch_html_retries_on_503_then_ok(mock_session):
    sess = MagicMock()
    fail = MagicMock()
    fail.raise_for_status.side_effect = requests.HTTPError(response=fail)
    fail.status_code = 503
    ok = MagicMock()
    ok.text = "<html>ok</html>"
    ok.raise_for_status = MagicMock()
    sess.get.side_effect = [fail, ok]
    mock_session.return_value = sess

    with patch("utils.fetcher.time.sleep"):
        assert fetch_html("https://example.edu/") == "<html>ok</html>"
    assert sess.get.call_count == 2


def test_fetch_html_no_retry_on_404(mock_session):
    sess = MagicMock()
    fail = MagicMock()
    fail.raise_for_status.side_effect = requests.HTTPError(response=fail)
    fail.status_code = 404
    sess.get.return_value = fail
    mock_session.return_value = sess

    assert fetch_html("https://example.edu/missing") is None
    sess.get.assert_called_once()


def test_fetch_html_retries_connection_error(mock_session):
    sess = MagicMock()
    ok = MagicMock()
    ok.text = "<html>ok</html>"
    ok.raise_for_status = MagicMock()
    sess.get.side_effect = [requests.ConnectionError("reset"), ok]
    mock_session.return_value = sess

    with patch("utils.fetcher.time.sleep"):
        out = fetch_html("https://example.edu/")
    assert out == "<html>ok</html>"
    assert sess.get.call_count == 2
