from scrapper_new.dates import find_first_iso_date_in_string, parse_date_iso, parse_http_date_header


def test_parse_date_iso_ymd():
    assert parse_date_iso("2026-04-05") == "2026-04-05"


def test_find_first_iso_in_blob():
    assert find_first_iso_date_in_string("Published 15/04/2026 for students") == "2026-04-15"


def test_parse_http_date_header():
    d = parse_http_date_header("Sat, 10 May 2026 08:00:00 GMT")
    assert d is not None
    assert d.year == 2026 and d.month == 5 and d.day == 10
