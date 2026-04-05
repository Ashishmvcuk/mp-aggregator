/**
 * @param {string} u
 */
function normalizeUrlKey(u) {
  const s = String(u || '').trim()
  if (!s) return ''
  try {
    const x = new URL(s)
    const path = x.pathname.replace(/\/$/, '') || '/'
    return `${x.hostname.toLowerCase()}${path.toLowerCase()}`
  } catch {
    return s.toLowerCase()
  }
}

/**
 * Manual rows first, then static; skip static rows whose link matches a manual row.
 * @param {Record<string, unknown>[]} manualItems
 * @param {Record<string, unknown>[]} staticItems
 * @param {'url' | 'result_url'} linkKey
 */
export function mergeWithManual(manualItems, staticItems, linkKey) {
  const seen = new Set()
  const out = []

  for (const item of manualItems) {
    if (!item || typeof item !== 'object') continue
    const link = item[linkKey] ?? item.url ?? item.result_url
    const k = normalizeUrlKey(link)
    if (!k) continue
    if (seen.has(k)) continue
    seen.add(k)
    out.push(item)
  }

  for (const item of staticItems) {
    if (!item || typeof item !== 'object') continue
    const link = item[linkKey] ?? item.url ?? item.result_url
    const k = normalizeUrlKey(link)
    if (!k) continue
    if (seen.has(k)) continue
    seen.add(k)
    out.push(item)
  }

  return out
}
