# MP University Results

Dashboard for **Madhya Pradesh university examination results** (and related links). The **React + Vite** frontend lives in [`website/`](website/); a **Python scraper** in [`scraper/`](scraper/) can refresh static JSON under `website/public/data/` for GitHub Pages or local preview.

## Repository layout

| Path | Purpose |
|------|---------|
| [`website/`](website/) | Vite + React app (`npm ci`, `npm run build` → `website/dist/`) |
| [`website/public/data/results.json`](website/public/data/results.json) | Results feed (`result_url`, `title`, `university`, `date`) — also written by the scraper when a run succeeds |
| [`scraper/`](scraper/) | Fetch → parse → normalize → dedupe → validate → output + optional sync to `website/public/data/` |
| [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) | Build from `website/` and publish `website/dist` to `gh-pages` |
| [`.github/workflows/scrape.yml`](.github/workflows/scrape.yml) | Scraper: fetch, validate JSON, sync `website/public/data/` (optional commit) |

## Frontend (website)

```bash
cd website
npm install
npm run dev
```

- **Production build:** `npm run build` → `website/dist/`
- **Preview:** `npm run preview`
- **Lint:** `npm run lint`

Open the URL shown in the terminal (usually `http://localhost:5173/`).

Data loading is implemented in `website/src/services/resultsService.js` (static JSON at `data/results.json` under the Vite `BASE_URL`).

## Scraper

See [`scraper/README.md`](scraper/README.md) for architecture, categories, and configuration.

Quick start:

```bash
cd scraper
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Validate output and CI:** see [`scraper/README.md`](scraper/README.md) (`validate_output.py`, `run_fixtures.py`, GitHub Actions `scrape.yml`).


Scheduled runs (default interval 5 minutes):

```bash
export SCRAPER_INTERVAL_SECONDS=300   # optional override
python scheduler.py
```

**Note:** CI does not run the scraper yet; refresh `website/public/data/` locally (or in another job) if you want the live site to pick up new JSON without committing manual edits.

## GitHub Pages

Project sites are served at `https://<user>.github.io/<repo>/`. In `website/vite.config.js`, set `repoName` to your GitHub repository name (default: `mp-aggregator`).

**Pages setup:** Settings → Pages → deploy from branch **`gh-pages`**, folder **`/`**.

The deploy workflow runs on pushes to **`main`**, installs npm dependencies in **`website/`**, builds, and publishes **`website/dist`** to **`gh-pages`** via [peaceiris/actions-gh-pages](https://github.com/peaceiris/actions-gh-pages).

---

© MP University Results — links point to official university sources; verify results on each institution’s portal.
