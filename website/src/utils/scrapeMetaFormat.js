/** Format ISO scrape timestamp for UI (UTC, human-readable). */
export function formatScrapedAtUtc(iso) {
  if (!iso || typeof iso !== 'string') return null
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso.slice(0, 19).replace('T', ' ')
  return `${d.toISOString().slice(0, 16).replace('T', ' ')} UTC`
}
