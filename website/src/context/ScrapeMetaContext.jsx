import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { fetchScrapeMeta } from '../services/dashboardDataService'

const ScrapeMetaContext = createContext({
  meta: null,
  loading: true,
})

export function ScrapeMetaProvider({ children }) {
  const [meta, setMeta] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    fetchScrapeMeta().then((m) => {
      if (!cancelled) {
        setMeta(m)
        setLoading(false)
      }
    })
    return () => {
      cancelled = true
    }
  }, [])

  const value = useMemo(() => ({ meta, loading }), [meta, loading])

  return <ScrapeMetaContext.Provider value={value}>{children}</ScrapeMetaContext.Provider>
}

export function useScrapeMeta() {
  return useContext(ScrapeMetaContext)
}
