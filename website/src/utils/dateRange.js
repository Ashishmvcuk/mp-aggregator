/**
 * @param {string} isoDateString YYYY-MM-DD
 * @param {number} days
 */
export function isWithinLastDays(isoDateString, days) {
  if (!isoDateString || typeof isoDateString !== 'string') return false
  const day = isoDateString.slice(0, 10)
  const t = new Date(`${day}T12:00:00Z`).getTime()
  if (Number.isNaN(t)) return false
  const cutoff = Date.now() - days * 86400000
  return t >= cutoff
}

/** Row has a non-empty announcement date from the source (Announced Date column). */
export function hasAnnouncedDate(item) {
  const d = item?.date
  return typeof d === 'string' && d.trim().length > 0
}

/** Prefer announcement date, else scrape index date (for sorting). */
export function feedSortKey(item) {
  return item.date || item.scrape_index_date || ''
}

/** @param {Array<{ date?: string; scrape_index_date?: string }>} items */
export function sortByDateDesc(items) {
  return [...items].sort((a, b) => feedSortKey(b).localeCompare(feedSortKey(a)))
}

/**
 * Sort by announcement `date` only (YYYY-MM-DD), descending. Rows missing `date` sort last.
 * Prefer {@link filterAndSortByAnnouncedDateDesc} when the list should exclude undated rows.
 * @param {Array<{ date?: string }>} items
 */
export function sortByAnnouncedDateDesc(items) {
  return [...items].sort((a, b) => {
    const da = typeof a?.date === 'string' ? a.date.trim().slice(0, 10) : ''
    const db = typeof b?.date === 'string' ? b.date.trim().slice(0, 10) : ''
    return db.localeCompare(da)
  })
}

/**
 * Keep rows with a non-empty announcement date; sort newest announcement first.
 * @param {Array<{ date?: string }>} items
 */
export function filterAndSortByAnnouncedDateDesc(items) {
  return sortByAnnouncedDateDesc(items.filter(hasAnnouncedDate))
}
