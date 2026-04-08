# Playwright / JS-rendered portals (optional future)

Some university sites render navigation links only after JavaScript runs. The default scraper uses `requests` + BeautifulSoup and does **not** execute JavaScript.

**If you need Playwright later:**

1. Add a separate CI job or script (not the default path) that runs a Chromium-based fetch for specific `seed_urls` only.
2. Cache HTML artifacts and feed them into the existing parser pipeline (same `Parser.parse(html, ...)` contract).
3. Expect higher runner time and memory; keep strict timeouts and rate limits.

No Playwright code ships in this repository yet; see backlog in [`RESEARCH_AND_BACKLOG.md`](RESEARCH_AND_BACKLOG.md).
