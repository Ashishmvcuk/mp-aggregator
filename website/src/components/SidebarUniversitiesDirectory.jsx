import { useIsMobileLayout } from '../hooks/useIsMobileLayout'
import './MobileCollapsibleTable.css'
import './SidebarUniversitiesDirectory.css'

/**
 * @param {{ portals: Array<{ university: string; url: string }> }} props
 */
export function SidebarUniversitiesDirectory({ portals }) {
  const mobile = useIsMobileLayout()
  const n = portals.length

  const table = (
    <div className="sr-uni__scroll">
      <table className="sr-uni__table">
        <thead>
          <tr>
            <th scope="col" className="sr-uni__th">
              University
            </th>
            <th scope="col" className="sr-uni__th sr-uni__th--link">
              Portal
            </th>
          </tr>
        </thead>
        <tbody>
          {portals.map((row) => (
            <tr key={row.url}>
              <td className="sr-uni__td sr-uni__td--name">
                <span className="sr-uni__name">{row.university}</span>
              </td>
              <td className="sr-uni__td sr-uni__td--link">
                <a
                  href={row.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="sr-uni__open"
                >
                  Visit
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )

  const body = (
    <>
      <p className="sr-uni__text">Official homepages of universities tracked by the scraper (same list as config).</p>
      {n === 0 ? (
        <p className="sr-uni__empty" role="status">
          No university list loaded yet. It appears after data sync from the project scraper.
        </p>
      ) : (
        table
      )}
    </>
  )

  if (mobile) {
    return (
      <aside className="sr-uni" id="university-portals" aria-label="University portal links">
        <details className="table-collapse sr-uni__details-wrap">
          <summary className="table-collapse__summary">
            <span className="table-collapse__summary-title">University portals</span>
            <span className="table-collapse__summary-meta">
              {n === 0 ? 'Tap to open' : `Tap to show ${n} universities`}
            </span>
          </summary>
          <div className="table-collapse__inner sr-uni__details-inner">{body}</div>
        </details>
      </aside>
    )
  }

  return (
    <aside className="sr-uni" id="university-portals" aria-label="University portal links">
      <h2 className="sr-uni__title">University portals</h2>
      {body}
    </aside>
  )
}
