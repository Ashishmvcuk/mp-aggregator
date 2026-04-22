import { useEffect, useState } from 'react'
import { useIsMobileLayout } from '../hooks/useIsMobileLayout'
import { formatAnnouncedDate } from '../utils/formatDate'
import { Pagination } from './Pagination'
import './FeedList.css'
import './MobileCollapsibleTable.css'

/**
 * @param {{
 *   title: string
 *   subtitle?: string
 *   id?: string
 *   items: Array<{ university: string; title: string; url: string; date?: string; scrape_index_date?: string }>
 *   emptyMessage?: string
 *   footer?: import('react').ReactNode
 *   disableMobileCollapse?: boolean
 *   pageSize?: number
 *   loadMoreIncrement?: number
 *   tallScroll?: boolean
 *   showAnnouncedDate?: boolean
 *   paginated?: boolean
 * }} props
 */
export function FeedList({
  title,
  subtitle,
  id,
  items,
  emptyMessage = 'Nothing to show yet.',
  footer = null,
  disableMobileCollapse = false,
  pageSize = 0,
  loadMoreIncrement = 20,
  tallScroll = false,
  showAnnouncedDate = true,
  paginated = false,
}) {
  const headingId = id ? `${id}-heading` : undefined
  const mobile = useIsMobileLayout()
  const useCollapse = mobile && !disableMobileCollapse
  const hasItems = items.length > 0

  /** How many times user clicked "Load more" after the first page. */
  const [extraLoadBatches, setExtraLoadBatches] = useState(0)
  /** Current 1-based page when paginated. */
  const [page, setPage] = useState(1)

  useEffect(() => {
    setExtraLoadBatches(0)
    setPage(1)
  }, [items])

  const usePaginator = paginated && pageSize > 0
  const pageCount = usePaginator ? Math.max(1, Math.ceil(items.length / pageSize)) : 1
  const safePage = Math.min(page, pageCount)

  let displayItems
  let visibleCap
  let canLoadMore = false
  let remaining = 0

  if (usePaginator) {
    const start = (safePage - 1) * pageSize
    const end = Math.min(items.length, start + pageSize)
    displayItems = items.slice(start, end)
    visibleCap = end
  } else if (pageSize > 0) {
    visibleCap = Math.min(items.length, pageSize + extraLoadBatches * loadMoreIncrement)
    displayItems = items.slice(0, visibleCap)
    canLoadMore = visibleCap < items.length
    remaining = Math.max(0, items.length - visibleCap)
  } else {
    displayItems = items
    visibleCap = items.length
  }

  const loadMore = () => {
    setExtraLoadBatches((b) => b + 1)
  }

  const scrollClassName = `feed-board__scroll${tallScroll ? ' feed-board__scroll--tall' : ''}`

  const tableBlock =
    items.length === 0 ? (
      <p className="feed-board__empty" role="status">
        {emptyMessage}
      </p>
    ) : (
      <div className={scrollClassName}>
        <table
          className={`feed-table${showAnnouncedDate ? '' : ' feed-table--no-date'}`}
        >
          <thead>
            <tr>
              {showAnnouncedDate ? (
                <th scope="col" className="feed-table__th feed-table__th--date">
                  Announced Date
                </th>
              ) : null}
              <th scope="col" className="feed-table__th">
                University
              </th>
              <th scope="col" className="feed-table__th">
                Title
              </th>
              <th scope="col" className="feed-table__th feed-table__th--link">
                Link
              </th>
            </tr>
          </thead>
          <tbody>
            {displayItems.map((r, i) => (
              <tr key={`${r.university}-${r.title}-${r.date || r.scrape_index_date}-${i}`}>
                {showAnnouncedDate ? (
                  <td className="feed-table__td feed-table__td--date" data-label="Announced Date">
                    {formatAnnouncedDate(r)}
                  </td>
                ) : null}
                <td className="feed-table__td" data-label="University">
                  {r.university}
                </td>
                <td className="feed-table__td" data-label="Title">
                  {r.title}
                </td>
                <td className="feed-table__td feed-table__td--link" data-label="Link">
                  <a
                    href={r.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="feed-table__link"
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

  const footerNode = footer ? <div className="feed-board__footer">{footer}</div> : null

  const loadMoreNode =
    canLoadMore ? (
      <div className="feed-board__load-more">
        <button type="button" className="feed-board__load-more-btn" onClick={loadMore}>
          Load more ({remaining} remaining)
        </button>
      </div>
    ) : null

  const paginationNode = usePaginator && hasItems ? (
    <Pagination
      page={safePage}
      pageCount={pageCount}
      onChange={setPage}
      totalItems={items.length}
      pageSize={pageSize}
      label={`${title} pagination`}
    />
  ) : null

  const countNote =
    pageSize > 0 && hasItems && !usePaginator ? (
      <p className="feed-board__count" role="status">
        Showing {displayItems.length} of {items.length}
      </p>
    ) : null

  if (useCollapse) {
    const rowWord = items.length === 1 ? 'row' : 'rows'
    return (
      <section
        className="feed-board feed-board--mobile-collapse"
        id={id}
        aria-labelledby={headingId}
      >
        <details className="table-collapse">
          <summary className="table-collapse__summary">
            <span className="table-collapse__summary-title" id={headingId}>
              {title}
            </span>
            <span className="table-collapse__summary-meta">
              {hasItems ? `Tap to show ${items.length} ${rowWord}` : 'Tap to open — empty'}
            </span>
          </summary>
          <div className="table-collapse__inner">
            {subtitle ? <p className="feed-board__note">{subtitle}</p> : null}
            {countNote}
            {tableBlock}
            {loadMoreNode}
            {paginationNode}
            {footerNode}
          </div>
        </details>
      </section>
    )
  }

  return (
    <section className="feed-board" id={id} aria-labelledby={headingId}>
      <h2 className="feed-board__title" id={headingId}>
        {title}
      </h2>
      {subtitle ? <p className="feed-board__note">{subtitle}</p> : null}
      {countNote}
      {tableBlock}
      {loadMoreNode}
      {paginationNode}
      {footerNode}
    </section>
  )
}
