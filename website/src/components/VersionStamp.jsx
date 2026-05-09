import { useScrapeMeta } from '../context/ScrapeMetaContext'
import { effectiveLastRunIso, formatScrapedAtUtc } from '../utils/scrapeMetaFormat'
import './VersionStamp.css'

export function VersionStamp() {
  const { meta, loading } = useScrapeMeta()

  const lastRunIso = effectiveLastRunIso(meta)
  if (loading || !lastRunIso) {
    return null
  }

  const label = formatScrapedAtUtc(lastRunIso)
  if (!label) return null

  return (
    <aside className="version-stamp" aria-label="Data last updated">
      <div className="version-stamp__updated">
        Date updated{' '}
        <time dateTime={String(lastRunIso)}>{label}</time>
      </div>
    </aside>
  )
}
