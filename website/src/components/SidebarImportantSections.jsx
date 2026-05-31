import { Link } from 'react-router-dom'
import { useIsMobileLayout } from '../hooks/useIsMobileLayout'
import { ImportantLinksList } from './ImportantLinksList'
import './MobileCollapsibleTable.css'
import './SidebarImportantSections.css'

/**
 * @param {{
 *   items: Array<{ category: string; organization: string; websitelink: string; logo?: string }>
 *   totalCount?: number
 *   placement?: 'sidebar' | 'mobile'
 * }} props
 */
export function SidebarImportantSections({ items, totalCount, placement = 'sidebar' }) {
  const mobile = useIsMobileLayout()
  const count = items.length
  const total = totalCount ?? count
  const showViewMore = total > count

  const tableOrEmpty =
    count === 0 ? (
      <p className="sr-imp__empty" role="status">
        No important links on file yet — add entries to <code>important_links.json</code>.
      </p>
    ) : (
      <ImportantLinksList items={items} compact />
    )

  const viewMore =
    total > 0 ? (
      <p className="sr-imp__more">
        <Link to="/important-links" className="sr-imp__more-link">
          {showViewMore ? `Show more (${total} links) →` : 'Important sections page →'}
        </Link>
      </p>
    ) : null

  if (placement === 'mobile' || mobile) {
    return (
      <aside
        className="sr-imp"
        id="important-sections"
        aria-label="Important national organization links"
      >
        <details className="table-collapse sr-imp__details-wrap">
          <summary className="table-collapse__summary">
            <span className="table-collapse__summary-title">Important sections</span>
            <span className="table-collapse__summary-meta">
              {total === 0
                ? 'Tap to open — no links yet'
                : count < total
                  ? `Showing ${count} of ${total} · tap to expand`
                  : `Tap to show ${count} link${count === 1 ? '' : 's'}`}
            </span>
          </summary>
          <div className="table-collapse__inner sr-imp__details-inner">
            {tableOrEmpty}
            {viewMore}
          </div>
        </details>
      </aside>
    )
  }

  return (
    <aside className="sr-imp" id="important-sections" aria-label="Important national organization links">
      <h2 className="sr-imp__title">Important sections</h2>
      {tableOrEmpty}
      {viewMore}
    </aside>
  )
}
