import { useScrapeMeta } from '../context/ScrapeMetaContext'
import { formatScrapedAtUtc } from '../utils/scrapeMetaFormat'
import './VersionStamp.css'

export function VersionStamp() {
  const { meta, loading } = useScrapeMeta()

  if (loading || !meta?.scrapedAt) {
    return null
  }

  const label = formatScrapedAtUtc(meta.scrapedAt)
  if (!label) return null

  return (
    <aside className="version-stamp" aria-label="Data last updated">
      <div className="version-stamp__updated">
        Date updated{' '}
        <time dateTime={String(meta.scrapedAt)}>{label}</time>
      </div>
    </aside>
  )
}
