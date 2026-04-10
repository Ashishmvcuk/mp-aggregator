import { useEffect, useMemo, useState } from 'react'
import { fetchScrapeMeta } from '../services/dashboardDataService'
import { fetchResults } from '../services/resultsService'

function normalizeUniversity(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '')
}

function normalizeHost(urlValue) {
  try {
    const host = new URL(String(urlValue || '')).hostname.toLowerCase()
    return host.startsWith('www.') ? host.slice(4) : host
  } catch {
    return ''
  }
}

/**
 * Loads results once; supports filtering by search query, selected university, and university type.
 * @param {string} searchQuery
 * @param {{
 *  typeFilter?: string
 *  selectedUniversity?: string
 *  referenceRows?: Array<{ university?: string; name?: string; url?: string; type?: string }>
 * }} [options]
 */
export function useResults(searchQuery, options = {}) {
  const {
    typeFilter = 'all',
    selectedUniversity = 'all',
    referenceRows = [],
  } = options
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

  const refByNormalized = useMemo(() => {
    const m = new Map()
    for (const row of referenceRows) {
      const uni = String(row?.university || row?.name || '').trim()
      if (!uni) continue
      const key = normalizeUniversity(uni)
      m.set(key, {
        type: String(row?.type || ''),
        host: normalizeHost(String(row?.url || '')),
      })
    }
    return m
  }, [referenceRows])

  const filtered = useMemo(() => {
    let rows = items

    if (typeFilter && typeFilter !== 'all' && refByNormalized.size > 0) {
      rows = rows.filter((r) => {
        const ref = refByNormalized.get(normalizeUniversity(r.university))
        return ref?.type === typeFilter
      })
    }
    if (selectedUniversity && selectedUniversity !== 'all') {
      const selectedNorm = normalizeUniversity(selectedUniversity)
      rows = rows.filter((r) => normalizeUniversity(r.university) === selectedNorm)
    }
    if (q) {
      rows = rows.filter(
        (r) =>
          r.university.toLowerCase().includes(q) || r.title.toLowerCase().includes(q)
      )
    }
    return rows.map((r) => {
      const ref = refByNormalized.get(normalizeUniversity(r.university))
      const resultHost = normalizeHost(r.result_url)
      const officialReferenceMatch = Boolean(ref && ref.host && resultHost && ref.host === resultHost)
      return { ...r, officialReferenceMatch }
    })
  }, [items, q, typeFilter, selectedUniversity, refByNormalized])

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
