import { useEffect, useMemo, useState } from 'react'
import { loadImportantLinks } from '../services/dashboardDataService'

/**
 * @typedef {Object} ImportantLink
 * @property {string} category
 * @property {string} organization
 * @property {string} websitelink
 * @property {string} [logo]
 */

export function useImportantLinks(searchQuery) {
  const [items, setItems] = useState(/** @type {ImportantLink[]} */ ([]))
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(/** @type {string|null} */ (null))

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    loadImportantLinks()
      .then((data) => {
        if (!cancelled) setItems(data)
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load important links')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const q = searchQuery.trim().toLowerCase()
  const filtered = useMemo(() => {
    if (!q) return items
    return items.filter(
      (r) =>
        (r.category && r.category.toLowerCase().includes(q)) ||
        (r.organization && r.organization.toLowerCase().includes(q))
    )
  }, [items, q])

  const titleSuggestions = useMemo(() => {
    const s = new Set()
    for (const r of items) {
      const t = (r.organization || '').trim()
      if (t.length >= 4) s.add(t)
      if (s.size >= 400) break
    }
    return [...s].sort((a, b) => a.localeCompare(b))
  }, [items])

  return { items, filtered, loading, error, titleSuggestions }
}
