import { useEffect, useMemo, useState } from 'react'
import { fetchResults } from '../services/resultsService'

/**
 * Loads results once; exposes optional client-side filter by university or title.
 */
export function useResults(searchQuery) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    fetchResults()
      .then((data) => {
        if (!cancelled) setItems(data)
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

  const summary = useMemo(() => computeSummary(items), [items])

  return { items, filtered, summary, loading, error }
}

function computeSummary(items) {
  const universities = new Set(items.map((r) => r.university))
  const dates = items.map((r) => r.date).filter(Boolean)
  const latest =
    dates.length > 0
      ? dates.reduce((a, b) => (a > b ? a : b))
      : null
  return {
    universityCount: universities.size,
    resultCount: items.length,
    latestDate: latest,
  }
}
