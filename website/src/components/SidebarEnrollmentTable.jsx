import { formatDateShort } from '../utils/formatDate'
import './SidebarEnrollmentTable.css'

/**
 * @param {{
 *   items: Array<{ university: string; title: string; url: string; date: string }>
 *   placement?: 'sidebar' | 'mobile'
 * }} props
 */
export function SidebarEnrollmentTable({ items, placement = 'sidebar' }) {
  const count = items.length

  const tableOrEmpty =
    count === 0 ? (
      <p className="sr-enroll__empty" role="status">
        No matching notices in the current news data — try again after the next scrape.
      </p>
    ) : (
      <div className="sr-enroll__scroll">
        <table className="sr-enroll__table">
          <thead>
            <tr>
              <th scope="col" className="sr-enroll__th sr-enroll__th--date">
                Date
              </th>
              <th scope="col" className="sr-enroll__th">
                Notice
              </th>
              <th scope="col" className="sr-enroll__th sr-enroll__th--link">
                Link
              </th>
            </tr>
          </thead>
          <tbody>
            {items.map((row, i) => (
              <tr key={`${row.url}-${row.date}-${i}`}>
                <td className="sr-enroll__td sr-enroll__td--date">{formatDateShort(row.date)}</td>
                <td className="sr-enroll__td sr-enroll__td--notice">
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
                <td className="sr-enroll__td sr-enroll__td--link">
                  <a
                    href={row.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="sr-enroll__open"
                  >
                    Open
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )

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
              {count === 0 ? 'Tap to open — no matches right now' : `Tap to show ${count} notices`}
            </span>
          </summary>
          <div className="sr-enroll__details-inner">
            <p className="sr-enroll__text">
              Latest from the news feed (enrollment / admission keywords). Same list as on desktop sidebar.
            </p>
            {tableOrEmpty}
          </div>
        </details>
      </aside>
    )
  }

  return (
    <aside className="sr-enroll" aria-label="Latest enrollment and admission notices">
      <h2 className="sr-enroll__title">Enrollment & admissions open</h2>
      <p className="sr-enroll__text">Ten latest notices from the news feed (enrollment / admission keywords).</p>
      {tableOrEmpty}
    </aside>
  )
}
