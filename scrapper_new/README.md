# scrapper_new — input-driven hub scraper

Fetches HTML for each URL listed in [`input_data/input_10.json`](../input_data/input_10.json) (or `--input`), extracts anchor-based updates, filters to a **rolling recency window** (default **60 days**, i.e. about two months), dedupes by **normalized title + URL**, and writes JSON under **`scrapper_new/output/`** by default — or under **`SCRAPPER_NEW_OUTPUT_DIR`** when that env var is set and `--output-dir` is omitted.

This package is **standalone** from [`scraper/`](../scraper/). To refresh the React app’s feeds locally (same layout as CI, using a gitignored scratch dir):

```bash
export SCRAPPER_NEW_OUTPUT_DIR="$PWD/output_data"
python3 -m scrapper_new --emit-website-buckets
python3 scrapper_new/scripts/sync_website_public_data.py
```

Without the env var, the two commands still default to `scrapper_new/output/`. The sync step also writes **`website/public/data/scrape_meta.json`** (`scrapedAt`, `websiteSyncAt`, `runId`, …) so the header **Last run** updates. Override with `--source` / `--run-summary` / `--dest` for ad-hoc paths.

### GitHub Actions

**Recommended:** run the **[`Scraper`](../.github/workflows/scrape.yml)** workflow (**Actions → Scraper → Run workflow**). It runs the legacy MP scraper, `sync_to_website.py`, then **`scrapper_new`** + **`sync_website_public_data.py`**, so **`website/public/data/`** gets the latest **`input_data/input_10.json`** feeds and **`scrape_meta.json`** in **one** job and **one** commit.

Optional standalone workflow: [`.github/workflows/scrapper_new.yml`](../.github/workflows/scrapper_new.yml) (**Actions → Scrapper new**) — same env (`SCRAPPER_NEW_OUTPUT_DIR` → `output_data`), but only scrapper_new + its commit script (no legacy scrape). **`output_data/`** stays gitignored.

## Install

From the repository root:

```bash
python3 -m venv .venv-scrapper-new
source .venv-scrapper-new/bin/activate
pip install -r scrapper_new/requirements.txt
```

## Run

```bash
cd /path/to/mp-aggregator
python3 -m scrapper_new
```

Options:

| Flag | Meaning |
|------|---------|
| `--input PATH` | Input JSON (default: `input_data/input_10.json` under `--repo-root`) |
| `--repo-root PATH` | Repo root (default: parent of this package) |
| `--output-dir PATH` | Output directory (default: `scrapper_new/output/`, or `SCRAPPER_NEW_OUTPUT_DIR` when set and flag omitted) |
| `--emit-website-buckets` | Also write `output/website_buckets/{results,news,...}.json` in the same shape as the React app’s feed rows |
| `--include-login-urls` | Also scrape `student_login_url` (default: **skipped**) |

Environment:

| Variable | Default | Meaning |
|----------|---------|---------|
| `SCRAPPER_NEW_OUTPUT_DIR` | (unset) | When set, default scrape output root (`input10_updates.json`, `run_summary.json`, `website_buckets/` live here). Sync defaults to `<this>/website_buckets` and `<this>/run_summary.json`. CI uses `…/output_data`. |
| `SCRAPPER_NEW_WORKERS` | `6` | Parallel fetch threads |
| `SCRAPPER_NEW_TIMEOUT` | `30` | Per-request timeout (seconds); falls back to `SCRAPER_FETCH_TIMEOUT` |
| `SCRAPPER_NEW_MAX_ATTEMPTS` | `3` | HTTP retries; falls back to `SCRAPER_FETCH_MAX_ATTEMPTS` |
| `SCRAPPER_NEW_RECENCY_DAYS` | `60` | Drop items whose effective `date` is before this many UTC calendar days ago |
| `SCRAPPER_NEW_FAST_FAIL_CONNECT` / `SCRAPER_FETCH_FAST_FAIL_CONNECT` | off | If truthy, do not retry connect/timeouts as aggressively |

## Output

Paths below are relative to the chosen output directory (default `scrapper_new/output/`, or `SCRAPPER_NEW_OUTPUT_DIR`).

- **`input10_updates.json`** — array of objects: `university`, `title`, `description`, `content_kind`, `category` (one of the seven site buckets), `url`, `date` (`YYYY-MM-DD`), `published_date_raw`, `date_confidence` (`high` / `medium` / `low`), `scraped_at`, `source_page_url`.
- **`run_summary.json`** — counts per university and totals (fetch OK/fail, skipped old / no signal / duplicate, items emitted).

### `date` and `date_confidence`

- **high**: Parsed announcement date from link or table context, on or after the recency cutoff.
- **medium**: No per-link date; **`Last-Modified`** on the fetched page is on or after the cutoff — the item’s `date` is set to that calendar day.
- **low**: No parseable date; title contains a **recent academic year** (current year ± 1). The item’s `date` is set to the **UTC run day** so it can still pass the dashboard’s `hasAnnouncedDate` check if you merge into `public/data/*.json`. Treat these rows cautiously.

### `content_kind` → website `category`

| content_kind | category (site bucket) |
|--------------|-------------------------|
| result | results |
| timetable, admit_card | admit_cards |
| syllabus | syllabus |
| admission, exam_form | enrollments |
| job | jobs |
| news, other | news |

### Website buckets (`--emit-website-buckets`)

Each file is an array of `{ university, title, url, date, category }` matching the canonical scraper record shape described in [`scraper/README.md`](../scraper/README.md).

## Logs

Console plus timestamped file under `scrapper_new/logs/` (e.g. `run_20260511T120000Z.log`).

## Tests

```bash
pip install -r scrapper_new/requirements-dev.txt
pytest scrapper_new/tests -q
```
