import { useMemo } from 'react'
import './ResultsTicker.css'

/**
 * @param {{ results: Array<{ university: string; title: string; result_url: string; date: string }>; loading?: boolean }} props
 */
export function ResultsTicker({ results, loading }) {
  const segments = useMemo(() => {
    if (!results?.length) return []
    return results.map((r, i) => ({
      key: `${r.university}-${r.title}-${r.date}-${i}`,
      university: r.university,
      title: r.title,
      url: r.result_url,
      date: r.date,
    }))
  }, [results])

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
          <span className="results-ticker__sep">·</span>
          <span className="results-ticker__date">{s.date}</span>
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
          <div className="results-ticker__marquee">
            {renderTrack('a', true)}
            {renderTrack('b', false)}
          </div>
        </div>
      </div>
    </div>
  )
}
