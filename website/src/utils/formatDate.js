/** @param {string | null | undefined} iso Date-only `YYYY-MM-DD` or full ISO datetime (e.g. scrape_meta `scrapedAt`). */
export function formatDateMedium(iso) {
  if (!iso) return '—'
  try {
    const s = String(iso).trim()
    const d = /^\d{4}-\d{2}-\d{2}$/.test(s) ? new Date(`${s}T12:00:00`) : new Date(s)
    return new Intl.DateTimeFormat('en-IN', {
      dateStyle: 'medium',
    }).format(d)
  } catch {
    return iso
  }
}

/** Sarkari-style short date for tables (dd/MM/yyyy). */
export function formatDateShort(iso) {
  if (!iso) return '—'
  try {
    return new Intl.DateTimeFormat('en-IN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    }).format(new Date(iso + 'T12:00:00'))
  } catch {
    return iso
  }
}
