# AGENTS.md

## Cursor Cloud specific instructions

This repo has three components (see `README.md`, `scraper/README.md`, `scrapper_new/README.md`):

- `website/` — Vite + React 19 dashboard (the user-facing product). Static JSON in `website/public/data/` is the data source.
- `scraper/` — legacy Python scraper that produces that JSON.
- `scrapper_new/` — newer input-driven Python scraper.

Dependencies (website npm packages + both scrapers' Python packages) are installed by the startup update script, so you normally don't need to install anything.

### Running / testing services

- **Website dev server:** `npm run dev` in `website/` (Vite, http://localhost:5173/). The app uses `HashRouter`, so routes are hash-based: home `#/`, results `#/results`, content admin `#/admin`.
- **Website lint / build:** `npm run lint` and `npm run build` in `website/`. Lint currently reports 2 pre-existing warnings (0 errors) — that is expected.
- **Scraper tests:** `cd scraper && python3 -m pytest tests/ -q`.
- **scrapper_new tests:** from repo root, `python3 -m pytest scrapper_new/tests -q`.
- Use `python3 -m pytest` (the `pytest` console script installs to `~/.local/bin`, which may not be on `PATH`).

### Non-obvious caveats

- **Content admin** (`#/admin`): local dev accepts demo credentials `admin` / `admin`. The "add manual entry" form only appears when Supabase env vars (`VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`) are set; without them the admin page shows "Database not connected (optional)" by design. For DB-free manual entries, edit `website/public/data/manual_additions.json`.
- **Live scraping needs outbound network** to MP university portals. The pytest suites run fully offline against fixtures; running `python main.py` / `python3 -m scrapper_new ...` actually fetches remote sites and may fail or be slow in a sandboxed environment.
- The root `package-lock.json` is a stub (no root `package.json`); all npm work happens inside `website/`.
