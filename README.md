# MP University Results

A small React (Vite) dashboard that lists **latest university examination result links** for Madhya Pradesh. Data is loaded from static JSON today; the same shape can later be filled by a scraper or API.

## Run locally

```bash
npm install
npm run dev
```

Open the URL shown in the terminal (usually `http://localhost:5173/`).

- **Production build:** `npm run build` → output in `dist/`
- **Preview production build:** `npm run preview`
- **Lint:** `npm run lint`

## Project layout

| Path | Purpose |
|------|---------|
| `public/results.json` | Mock data (`university`, `title`, `result_url`, `date`) |
| `src/services/resultsService.js` | Data loading — swap for API later |
| `src/hooks/useResults.js` | Fetch + search filter + summary metrics |
| `src/pages/HomePage.jsx` | Page composition |
| `src/components/` | `Header`, `SearchBar`, `SummaryCards`, `ResultsList`, `ResultTableRow`, `SidebarQuickLinks`, `DashboardChart`, `Footer` |

## GitHub Pages (free hosting)

### 1. Repository name and Vite `base`

GitHub project sites are served at `https://<user>.github.io/<repo>/`. The app must load assets from that subpath.

In `vite.config.js`, set `repoName` to **your GitHub repository name** (default here is `mp-aggregator`):

```js
const repoName = 'mp-aggregator'
```

`base` is `/` during `npm run dev` and `/<repoName>/` for production builds.

### 2. Enable GitHub Pages

1. Push this repo to GitHub.
2. **Settings → Pages**
3. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
4. Choose branch **`gh-pages`**, folder **`/`** (root), then save.

The first deploy is created by the workflow below after you push to `main`.

### 3. GitHub Actions deploy

Workflow: [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml).

- **Trigger:** push to `main`
- **Steps:** `npm ci` → `npm run build` → publish `dist/` to the **`gh-pages`** branch via [peaceiris/actions-gh-pages](https://github.com/peaceiris/actions-gh-pages).

The workflow uses `GITHUB_TOKEN` (no extra secrets). `permissions: contents: write` allows pushing to `gh-pages`.

After a successful run, the site is available at:

`https://<your-username>.github.io/<repo-name>/`

---

© MP University Results — links point to official university sources; verify results on each institution’s portal.
