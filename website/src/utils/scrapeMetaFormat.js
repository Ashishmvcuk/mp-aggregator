/** Prefer post-sync stamp so “Last run” advances when feeds are unchanged but sync ran. */
export function effectiveLastRunIso(meta) {
  if (!meta || typeof meta !== 'object') return null
  const ws = meta.websiteSyncAt
  const sa = meta.scrapedAt
  if (typeof ws === 'string' && ws.trim()) return ws
  if (typeof sa === 'string' && sa.trim()) return sa
  return null
}

/** Format ISO scrape timestamp for UI (UTC, human-readable, seconds). */
export function formatScrapedAtUtc(iso) {
  if (!iso || typeof iso !== 'string') return null
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso.slice(0, 19).replace('T', ' ')
  return `${d.toISOString().slice(0, 19).replace('T', ' ')} UTC`
}
