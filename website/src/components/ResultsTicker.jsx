import { useLayoutEffect, useMemo, useRef, useState } from 'react'
import { formatAnnouncedDate } from '../utils/formatDate'
import './ResultsTicker.css'

const LOGOS_BASE = `${import.meta.env.BASE_URL}data/logos/`

/** Max items in the strip (full list still on the results page). */
const MAX_TICKER_ITEMS = 40
/** Target scroll speed so duration scales when content width changes (px per second). */
const SCROLL_PX_PER_SEC = 90
/** Short logo strips were stuck at 45s minimum — keep a low floor so few items still move. */
const MIN_SCROLL_DURATION_S = 10
const MAX_SCROLL_DURATION_S = 7200
/** Before first layout measure. */
const DEFAULT_SCROLL_DURATION_S = 24

function parseAnnouncedDateTs(r) {
  const s = typeof r.date === 'string' ? r.date.trim().slice(0, 10) : ''
  const t = Date.parse(`${s}T12:00:00Z`)
  return Number.isNaN(t) ? 0 : t
}

/**
 * @param {{ results: Array<{ tooltipTitle?: string; url?: string; logo?: string; university?: string; title?: string; result_url?: string; date?: string; scrape_index_date?: string }>; loading?: boolean }} props
 */
export function ResultsTicker({ results, loading }) {
  const marqueeRef = useRef(null)
  const [scrollDurationS, setScrollDurationS] = useState(DEFAULT_SCROLL_DURATION_S)

  const segments = useMemo(() => {
    if (!results?.length) return []
    const sorted = [...results].sort((a, b) => parseAnnouncedDateTs(b) - parseAnnouncedDateTs(a))
    return sorted
      .slice(0, MAX_TICKER_ITEMS)
      .map((r, i) => {
        const tooltipTitle = r.tooltipTitle || r.university || r.title || 'Link'
        const href = r.url || r.result_url || ''
        const logoFile = typeof r.logo === 'string' ? r.logo.trim() : ''
        const displayTitle = typeof r.title === 'string' ? r.title.trim() : ''
        return {
          key: `${tooltipTitle}-${logoFile || displayTitle}-${r.date || r.scrape_index_date}-${i}`,
          tooltipTitle,
          href,
          logoSrc: logoFile ? `${LOGOS_BASE}${logoFile}` : '',
          displayTitle,
          university: r.university,
          title: displayTitle,
          dateLabel: formatAnnouncedDate(r),
        }
      })
      .filter((s) => s.href)
  }, [results])

  useLayoutEffect(() => {
    if (!segments.length) return undefined

    const measure = () => {
      const root = marqueeRef.current
      if (!root) return
      const track = root.querySelector('.results-ticker__track')
      if (!track) return
      const w = track.scrollWidth
      if (w <= 0) return
      const seconds = w / SCROLL_PX_PER_SEC
      const clamped = Math.min(
        MAX_SCROLL_DURATION_S,
        Math.max(MIN_SCROLL_DURATION_S, seconds),
      )
      setScrollDurationS(clamped)
    }

    measure()
    const root = marqueeRef.current
    if (!root) return undefined
    const ro = new ResizeObserver(() => measure())
    ro.observe(root)
    return () => ro.disconnect()
  }, [segments])

  if (loading) {
    return (
      <div className="results-ticker results-ticker--loading" role="status" aria-live="polite">
        <div className="results-ticker__inner">
          <span className="results-ticker__label">Live feed</span>
          <span className="results-ticker__loading-text">Loading latest…</span>
        </div>
      </div>
    )
  }

  if (!segments.length) {
    return null
  }

  const renderTrack = (suffix, tabbable) => (
    <div
      className={`results-ticker__track results-ticker__track--${suffix}`}
      aria-hidden={tabbable ? undefined : true}
    >
      {segments.map((s) => (
        <a
          key={`${s.key}-${suffix}`}
          href={s.href}
          target="_blank"
          rel="noopener noreferrer"
          className={`results-ticker__item${s.logoSrc ? ' results-ticker__item--logo' : ''}`}
          title={s.tooltipTitle}
          aria-label={
            s.displayTitle && s.displayTitle !== s.tooltipTitle
              ? `${s.tooltipTitle} — ${s.displayTitle}`
              : s.tooltipTitle
          }
          tabIndex={tabbable ? undefined : -1}
        >
          {s.logoSrc ? (
            <>
              <img
                className="results-ticker__logo"
                src={s.logoSrc}
                alt=""
                width={48}
                height={28}
                loading="lazy"
                decoding="async"
              />
              {s.displayTitle ? (
                <span className="results-ticker__title results-ticker__title--after-logo">
                  {s.displayTitle}
                </span>
              ) : null}
            </>
          ) : (
            <>
              {s.university ? <span className="results-ticker__uni">{s.university}</span> : null}
              {s.university && s.title ? <span className="results-ticker__sep">·</span> : null}
              {s.title ? <span className="results-ticker__title">{s.title}</span> : null}
              {s.dateLabel ? (
                <>
                  <span className="results-ticker__sep">·</span>
                  <span className="results-ticker__date">{s.dateLabel}</span>
                </>
              ) : null}
            </>
          )}
        </a>
      ))}
    </div>
  )

  return (
    <div className="results-ticker" role="region" aria-label="Scrolling latest links">
      <div className="results-ticker__highlight" aria-hidden />
      <div className="results-ticker__inner">
        <span className="results-ticker__label">Latest</span>
        <div className="results-ticker__viewport">
          <div
            ref={marqueeRef}
            className="results-ticker__marquee"
            style={{ animationDuration: `${scrollDurationS}s` }}
          >
            {renderTrack('a', true)}
            {renderTrack('b', false)}
          </div>
        </div>
      </div>
    </div>
  )
}
