import { useEffect, useMemo, useState } from 'react'
import { fetchScrapeMeta } from '../services/dashboardDataService'
import { fetchResults } from '../services/resultsService'

/**
 * Loads results once; exposes optional client-side filter by university or title.
 */
export function useResults(searchQuery) {
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
    if (!q) return items
    return items.filter(
      (r) =>
        r.university.toLowerCase().includes(q) || r.title.toLowerCase().includes(q)
    )
  }, [items, q])

  const summary = useMemo(() => computeSummary(items, scrapedAt), [items, scrapedAt])

  return { items, filtered, summary, loading, error }
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
