import { useEffect, useMemo, useState } from 'react'
import { fetchScrollLatest } from '../services/scrollLatestService'
import { sortByAnnouncedDateDesc } from '../utils/dateRange'

/**
 * Loads curated ticker rows from `scroll_latest.json`.
 */
export function useScrollLatest() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    fetchScrollLatest()
      .then((data) => {
        if (!cancelled) setItems(data)
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load scroll latest')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const sorted = useMemo(() => sortByAnnouncedDateDesc(items), [items])

  return { items: sorted, loading, error }
}
