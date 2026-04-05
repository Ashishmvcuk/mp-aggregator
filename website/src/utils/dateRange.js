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

/** @param {Array<{ date?: string }>} items */
export function sortByDateDesc(items) {
  return [...items].sort((a, b) => (b.date || '').localeCompare(a.date || ''))
}
