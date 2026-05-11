from scrapper_new.pipeline import _dedupe_key  # noqa: SLF001


def test_dedupe_key_casefold():
    assert _dedupe_key("Hello World", "https://x/a") == _dedupe_key("hello  world", "https://x/a")


def test_dedupe_key_distinct_url():
    assert _dedupe_key("Same", "https://a") != _dedupe_key("Same", "https://b")
