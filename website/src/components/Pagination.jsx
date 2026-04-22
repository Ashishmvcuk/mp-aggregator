import './Pagination.css'

/**
 * Build a compact list of pages with ellipses, e.g.
 *   1 … 4 5 [6] 7 8 … 20
 * @param {number} current
 * @param {number} total
 * @param {number} [siblings=1]
 * @returns {(number|'…')[]}
 */
function buildPageWindow(current, total, siblings = 1) {
  if (total <= 7 + siblings * 2) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }
  const left = Math.max(2, current - siblings)
  const right = Math.min(total - 1, current + siblings)
  const out = [1]
  if (left > 2) out.push('…')
  for (let p = left; p <= right; p++) out.push(p)
  if (right < total - 1) out.push('…')
  out.push(total)
  return out
}

/**
 * @param {{
 *   page: number
 *   pageCount: number
 *   onChange: (p: number) => void
 *   totalItems?: number
 *   pageSize?: number
 *   label?: string
 * }} props
 */
export function Pagination({ page, pageCount, onChange, totalItems, pageSize, label = 'Pagination' }) {
  if (pageCount <= 1) return null

  const pages = buildPageWindow(page, pageCount)
  const prev = () => onChange(Math.max(1, page - 1))
  const next = () => onChange(Math.min(pageCount, page + 1))

  const rangeStart = pageSize ? (page - 1) * pageSize + 1 : null
  const rangeEnd =
    pageSize && totalItems != null ? Math.min(totalItems, page * pageSize) : null

  return (
    <nav className="sr-pager" aria-label={label}>
      {rangeStart != null && rangeEnd != null && totalItems != null && (
        <span className="sr-pager__range">
          Showing <strong>{rangeStart}</strong>–<strong>{rangeEnd}</strong> of{' '}
          <strong>{totalItems}</strong>
        </span>
      )}
      <ul className="sr-pager__list">
        <li>
          <button
            type="button"
            className="sr-pager__btn sr-pager__btn--step"
            onClick={prev}
            disabled={page === 1}
            aria-label="Previous page"
          >
            ‹ Prev
          </button>
        </li>
        {pages.map((p, i) =>
          p === '…' ? (
            <li key={`gap-${i}`} className="sr-pager__gap" aria-hidden>
              …
            </li>
          ) : (
            <li key={p}>
              <button
                type="button"
                className={`sr-pager__btn${p === page ? ' sr-pager__btn--active' : ''}`}
                onClick={() => onChange(p)}
                aria-current={p === page ? 'page' : undefined}
                aria-label={`Go to page ${p}`}
              >
                {p}
              </button>
            </li>
          )
        )}
        <li>
          <button
            type="button"
            className="sr-pager__btn sr-pager__btn--step"
            onClick={next}
            disabled={page === pageCount}
            aria-label="Next page"
          >
            Next ›
          </button>
        </li>
      </ul>
    </nav>
  )
}
