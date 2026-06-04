/**
 * Curated rows for the home-page "Latest" scrolling ticker.
 * Static file: `website/public/data/scroll_latest.json`
 */

const LOCAL_JSON_PATH = `${import.meta.env.BASE_URL}data/scroll_latest.json`

/**
 * @typedef {Object} ScrollLatestItem
 * @property {string} tooltipTitle
 * @property {string} url
 * @property {string} [logo]
 * @property {string} [university]
 * @property {string} [title]
 * @property {string} [date]
 */

function normalizeExternalUrl(raw) {
  const s = typeof raw === 'string' ? raw.trim() : ''
  if (!s) return ''
  if (/^https?:\/\//i.test(s)) return s
  return `https://${s}`
}

/**
 * @returns {Promise<ScrollLatestItem[]>}
 */
export async function fetchScrollLatest() {
  const base = LOCAL_JSON_PATH
  const sep = base.includes('?') ? '&' : '?'
  const url = `${base}${sep}_=${Date.now()}`
  const res = await fetch(url, { cache: 'no-store' })
  if (!res.ok) {
    throw new Error(`Failed to load scroll latest: ${res.status}`)
  }
  const data = await res.json()
  if (!Array.isArray(data)) {
    throw new Error('Invalid scroll_latest payload: expected an array')
  }
  return data.map((row) => ({
    tooltipTitle:
      row['tooltip-title'] ||
      row.tooltipTitle ||
      row['tip-title'] ||
      row.university ||
      row.title ||
      '',
    url: normalizeExternalUrl(row.url || row.result_url || ''),
    logo: typeof row.logo === 'string' ? row.logo.trim() : '',
    university: row.university,
    title: typeof row.title === 'string' ? row.title.trim() : '',
    date: row.date,
    scrape_index_date: row.scrape_index_date,
  }))
}
