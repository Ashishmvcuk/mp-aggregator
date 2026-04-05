/**
 * Static JSON under `public/data/` (synced by scraper).
 */

function dataUrl(path) {
  const base = import.meta.env.BASE_URL || '/'
  const p = path.replace(/^\//, '')
  return `${base}${p}`
}

/**
 * @param {string} path e.g. `data/news.json`
 * @returns {Promise<Array<Record<string, unknown>>>}
 */
export async function fetchJsonArray(path) {
  try {
    const res = await fetch(dataUrl(path))
    if (!res.ok) return []
    const data = await res.json()
    return Array.isArray(data) ? data : []
  } catch {
    return []
  }
}

/**
 * Runtime scrape metadata (`public/data/scrape_meta.json`), updated when CI/local sync runs.
 * @returns {Promise<Record<string, unknown> | null>}
 */
export async function fetchScrapeMeta() {
  try {
    const res = await fetch(dataUrl('data/scrape_meta.json'), { cache: 'no-store' })
    if (!res.ok) return null
    const data = await res.json()
    if (!data || typeof data !== 'object' || Array.isArray(data)) return null
    return data
  } catch {
    return null
  }
}

export function loadDashboardFeeds() {
  return Promise.all([
    fetchJsonArray('data/news.json'),
    fetchJsonArray('data/blogs.json'),
    fetchJsonArray('data/jobs.json'),
  ]).then(([news, blogs, jobs]) => ({ news, blogs, jobs }))
}

/** All category feeds used on the landing page (except results — loaded separately). */
export function loadLandingFeeds() {
  return Promise.all([
    fetchJsonArray('data/news.json'),
    fetchJsonArray('data/jobs.json'),
    fetchJsonArray('data/syllabus.json'),
    fetchJsonArray('data/admit_cards.json'),
    fetchJsonArray('data/blogs.json'),
  ]).then(([news, jobs, syllabus, admit_cards, blogs]) => ({
    news,
    jobs,
    syllabus,
    admit_cards,
    blogs,
  }))
}

export function loadAdmitCards() {
  return fetchJsonArray('data/admit_cards.json')
}
