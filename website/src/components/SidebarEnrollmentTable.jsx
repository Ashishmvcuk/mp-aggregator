import { Link } from 'react-router-dom'
import { formatDateShort } from '../utils/formatDate'
import './SidebarEnrollmentTable.css'

/**
 * @param {{
 *   items: Array<{ university: string; title: string; url: string; date: string }>
 *   totalCount?: number
 *   placement?: 'sidebar' | 'mobile'
 * }} props
 */
export function SidebarEnrollmentTable({ items, totalCount, placement = 'sidebar' }) {
  const count = items.length
  const total = totalCount ?? count
  const showViewMore = total > count

  const tableOrEmpty =
    count === 0 ? (
      <p className="sr-enroll__empty" role="status">
        No enrollment links in <code>enrollments.json</code> yet — run the scraper and sync, or add rows under{' '}
        <code>manual_additions.json</code> → <code>enrollments</code>.
      </p>
    ) : (
      <div className="sr-enroll__scroll">
        <table className="sr-enroll__table">
          <tbody>
            {items.map((row, i) => (
              <tr key={`${row.url}-${row.date}-${i}`}>
                <td className="sr-enroll__notice-cell">
                  <span className="sr-enroll__date">{formatDateShort(row.date)}</span>
                  <span className="sr-enroll__uni">{row.university}</span>
                  <a
                    href={row.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="sr-enroll__title-link"
                  >
                    {row.title}
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )

  const viewMore =
    total > 0 ? (
      <p className="sr-enroll__more">
        <Link to="/enrollments" className="sr-enroll__more-link">
          {showViewMore ? `View all ${total} enrollments →` : 'Enrollments page (search) →'}
        </Link>
      </p>
    ) : null

  if (placement === 'mobile') {
    return (
      <aside
        className="sr-enroll sr-enroll--mobile"
        id="enrollment-open"
        aria-label="Latest enrollment and admission notices"
      >
        <details className="sr-enroll__details">
          <summary className="sr-enroll__summary">
            <span className="sr-enroll__summary-title">Enrollment & admissions open</span>
            <span className="sr-enroll__summary-meta">
              {total === 0
                ? 'Tap to open — no links yet'
                : count < total
                  ? `Showing ${count} of ${total} · tap to expand`
                  : `Tap to show ${count} notice${count === 1 ? '' : 's'}`}
            </span>
          </summary>
          <div className="sr-enroll__details-inner">
            <p className="sr-enroll__text">
              Scraped <code>enrollments</code> bucket (admission / enrollment keywords). Manual rows merge here too.
            </p>
            {tableOrEmpty}
            {viewMore}
          </div>
        </details>
      </aside>
    )
  }

  return (
    <aside className="sr-enroll" aria-label="Latest enrollment and admission notices">
      <h2 className="sr-enroll__title">Enrollment & admissions open</h2>
      {tableOrEmpty}
      {viewMore}
    </aside>
  )
}
