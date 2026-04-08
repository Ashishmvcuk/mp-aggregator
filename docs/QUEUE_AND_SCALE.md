# Queue-based scraping (future)

The current design runs **one GitHub Actions job** that scrapes all configured universities sequentially in [`main.py`](../scraper/main.py). That is simple and cheap.

**If you outgrow a single runner:** split work by publishing fetch jobs to a queue (Cloud Tasks, Pub/Sub, or GitHub `matrix` strategy with shards of `universities.json`). Workers write JSON fragments to object storage; a final step merges, validates, and runs the existing `sync_to_website.py` + site build. The React app and static JSON contract stay the same.
