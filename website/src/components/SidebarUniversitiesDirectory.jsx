import { useMemo } from 'react'
import { useIsMobileLayout } from '../hooks/useIsMobileLayout'
import './MobileCollapsibleTable.css'
import './SidebarUniversitiesDirectory.css'

/**
 * @param {{ portals: Array<{ university: string; url: string }>; filterQuery?: string }} props
 */
export function SidebarUniversitiesDirectory({ portals, filterQuery = '' }) {
  const mobile = useIsMobileLayout()
  const q = filterQuery.trim().toLowerCase()
  const filtered = useMemo(() => {
    if (!q) return portals
    return portals.filter((p) => p.university.toLowerCase().includes(q))
  }, [portals, q])
  const n = filtered.length
  const total = portals.length

  const table = (
    <div className="sr-uni__scroll">
      <table className="sr-uni__table">
        <tbody>
          {filtered.map((row) => (
            <tr key={row.url}>
              <td className="sr-uni__td">
                <a
                  href={row.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="sr-uni__link"
                >
                  {row.university}
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
      {total === 0 ? (
        <p className="sr-uni__empty" role="status">
          No university list loaded yet. It appears after data sync from the project scraper.
        </p>
      ) : n === 0 ? (
        <p className="sr-uni__empty" role="status">
          No universities match “{filterQuery.trim()}”. Clear the search to see all {total} portals.
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
              {total === 0 ? 'Tap to open' : `Tap to show ${q ? `${n} of ${total}` : n} universities`}
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
