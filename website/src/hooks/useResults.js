import { useEffect, useMemo, useState } from 'react'
import { fetchScrapeMeta } from '../services/dashboardDataService'
import { fetchResults } from '../services/resultsService'

/**
 * Loads results once; optional filter by university or title, and by config `group` (when map provided).
 * @param {string} searchQuery
 * @param {{ groupFilter?: string; universityToGroup?: Map<string, string> }} [options]
 */
export function useResults(searchQuery, options = {}) {
  const { groupFilter = 'all', universityToGroup = new Map() } = options
  const [items, setItems] = useState([])
  const [scrapedAt, setScrapedAt] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    Promise.all([fetchResults(), fetchScrapeMeta()])
      .then(([data, meta]) => {
        if (!cancelled) {
          setItems(data)
          const raw = meta && typeof meta.scrapedAt === 'string' ? meta.scrapedAt : null
          setScrapedAt(raw)
        }
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load data')
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
    let rows = items
    if (groupFilter && groupFilter !== 'all' && universityToGroup.size > 0) {
      rows = rows.filter((r) => universityToGroup.get(r.university) === groupFilter)
    }
    if (!q) return rows
    return rows.filter(
      (r) =>
        r.university.toLowerCase().includes(q) || r.title.toLowerCase().includes(q)
    )
  }, [items, q, groupFilter, universityToGroup])

  const summary = useMemo(() => computeSummary(filtered, scrapedAt), [filtered, scrapedAt])

  const universityNames = useMemo(() => {
    const s = new Set(items.map((r) => r.university).filter(Boolean))
    return [...s].sort((a, b) => a.localeCompare(b))
  }, [items])

  const titleSuggestions = useMemo(() => {
    const s = new Set()
    for (const r of items) {
      const t = (r.title || '').trim()
      if (t.length >= 4) s.add(t)
      if (s.size >= 400) break
    }
    return [...s].sort((a, b) => a.localeCompare(b))
  }, [items])

  return { items, filtered, summary, loading, error, universityNames, titleSuggestions }
}

function computeSummary(items, scrapedAtIso) {
  const universities = new Set(items.map((r) => r.university))
  const dates = items.map((r) => r.date).filter(Boolean)
  const latestFromItems =
    dates.length > 0
      ? dates.reduce((a, b) => (a > b ? a : b))
      : null
  // Show last scraper sync time when available; else newest result row date.
  const latestDate = scrapedAtIso || latestFromItems
  return {
    universityCount: universities.size,
    resultCount: items.length,
    latestDate,
  }
}
