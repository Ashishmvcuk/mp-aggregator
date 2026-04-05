import { useScrapeMeta } from '../context/ScrapeMetaContext'
import { formatScrapedAtUtc } from '../utils/scrapeMetaFormat'
import { BUILD_TIME_LABEL, SCRAPER_VERSION_LABEL, SITE_VERSION_LABEL } from '../version'
import './VersionStamp.css'

function scraperLabelFromMeta(meta) {
  const v = meta?.scraperVersion
  if (v == null || v === '') return null
  const s = String(v).trim()
  return s.startsWith('v') ? `Scraper ${s}` : `Scraper v${s}`
}

export function VersionStamp() {
  const { meta } = useScrapeMeta()

  const scraperLine = scraperLabelFromMeta(meta) ?? `Scraper ${SCRAPER_VERSION_LABEL}`
  const dataUpdated = meta?.scrapedAt ? formatScrapedAtUtc(meta.scrapedAt) : null
  const runRef =
    meta?.runId != null && String(meta.runId).trim() !== ''
      ? String(meta.runId).trim()
      : null
  const ciRef =
    meta?.ciRunId != null && String(meta.ciRunId).trim() !== ''
      ? String(meta.ciRunId).trim()
      : null

  return (
    <aside className="version-stamp" aria-label="Application version">
      <div className="version-stamp__site">{SITE_VERSION_LABEL}</div>
      <div className="version-stamp__scraper">{scraperLine}</div>
      {dataUpdated ? (
        <div className="version-stamp__data">
          Data updated <time dateTime={String(meta.scrapedAt)}>{dataUpdated}</time>
        </div>
      ) : null}
      {runRef || ciRef ? (
        <div className="version-stamp__run">
          {runRef ? <>Run {runRef}</> : null}
          {runRef && ciRef ? ' · ' : null}
          {ciRef ? <>CI {ciRef}</> : null}
        </div>
      ) : null}
      {BUILD_TIME_LABEL ? (
        <time className="version-stamp__time" dateTime={BUILD_TIME_LABEL}>
          Build {BUILD_TIME_LABEL.slice(0, 10)}
        </time>
      ) : null}
    </aside>
  )
}
