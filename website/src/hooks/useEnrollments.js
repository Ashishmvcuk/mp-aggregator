import { useEffect, useMemo, useState } from 'react'
import { loadEnrollments } from '../services/dashboardDataService'
import { sortByDateDesc } from '../utils/dateRange'

/**
 * @typedef {Object} FeedItem
 * @property {string} university
 * @property {string} title
 * @property {string} url
 * @property {string} date
 */

export function useEnrollments(searchQuery) {
  const [items, setItems] = useState(/** @type {FeedItem[]} */ ([]))
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(/** @type {string|null} */ (null))

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    loadEnrollments()
      .then((data) => {
        if (!cancelled) setItems(sortByDateDesc(data))
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load enrollments')
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
        (r.university && r.university.toLowerCase().includes(q)) ||
        (r.title && r.title.toLowerCase().includes(q))
    )
  }, [items, q])

  return { items, filtered, loading, error }
}
