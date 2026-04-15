import { useLayoutEffect, useMemo, useRef, useState } from 'react'
import { formatAnnouncedDate } from '../utils/formatDate'
import './ResultsTicker.css'

/** Max items in the strip (full list still on the results page). */
const MAX_TICKER_ITEMS = 40
/** Target scroll speed so duration scales when content width changes (px per second). */
const SCROLL_PX_PER_SEC = 38
/** Avoid unusably fast or slow loops if measurement glitches. */
const MIN_SCROLL_DURATION_S = 45
const MAX_SCROLL_DURATION_S = 7200
/** Before first layout measure. */
const DEFAULT_SCROLL_DURATION_S = 180

function parseResultSortKey(r) {
  const ann = r.date
  const idx = r.scrape_index_date
  const s = ann || idx || ''
  const t = Date.parse(String(s))
  return Number.isNaN(t) ? 0 : t
}

/**
 * @param {{ results: Array<{ university: string; title: string; result_url: string; date?: string; scrape_index_date?: string }>; loading?: boolean }} props
 */
export function ResultsTicker({ results, loading }) {
  const marqueeRef = useRef(null)
  const [scrollDurationS, setScrollDurationS] = useState(DEFAULT_SCROLL_DURATION_S)

  const segments = useMemo(() => {
    if (!results?.length) return []
    const sorted = [...results].sort((a, b) => parseResultSortKey(b) - parseResultSortKey(a))
    const capped = sorted.slice(0, MAX_TICKER_ITEMS)
    return capped.map((r, i) => ({
      key: `${r.university}-${r.title}-${r.date || r.scrape_index_date}-${i}`,
      university: r.university,
      title: r.title,
      url: r.result_url,
      dateLabel: formatAnnouncedDate(r),
    }))
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
          <span className="results-ticker__loading-text">Loading latest results…</span>
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
          href={s.url}
          target="_blank"
          rel="noopener noreferrer"
          className="results-ticker__item"
          tabIndex={tabbable ? undefined : -1}
        >
          <span className="results-ticker__uni">{s.university}</span>
          <span className="results-ticker__sep">·</span>
          <span className="results-ticker__title">{s.title}</span>
          {s.dateLabel ? (
            <>
              <span className="results-ticker__sep">·</span>
              <span className="results-ticker__date">{s.dateLabel}</span>
            </>
          ) : null}
        </a>
      ))}
    </div>
  )

  return (
    <div className="results-ticker" role="region" aria-label="Scrolling latest examination results">
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
