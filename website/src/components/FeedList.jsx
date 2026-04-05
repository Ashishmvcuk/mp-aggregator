import './FeedList.css'

/**
 * @param {{ title: string; subtitle?: string; id?: string; items: Array<{ university: string; title: string; url: string; date: string }>; emptyMessage?: string; footer?: import('react').ReactNode }} props
 */
export function FeedList({ title, subtitle, id, items, emptyMessage = 'Nothing to show yet.', footer = null }) {
  const headingId = id ? `${id}-heading` : undefined
  return (
    <section className="feed-board" id={id} aria-labelledby={headingId}>
      <h2 className="feed-board__title" id={headingId}>
        {title}
      </h2>
      {subtitle ? <p className="feed-board__note">{subtitle}</p> : null}

      {items.length === 0 ? (
        <p className="feed-board__empty" role="status">
          {emptyMessage}
        </p>
      ) : (
        <div className="feed-board__scroll">
          <table className="feed-table">
            <thead>
              <tr>
                <th scope="col" className="feed-table__th feed-table__th--date">
                  Date
                </th>
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
              {items.map((r, i) => (
                <tr key={`${r.university}-${r.title}-${r.date}-${i}`}>
                  <td className="feed-table__td feed-table__td--date">{r.date}</td>
                  <td className="feed-table__td">{r.university}</td>
                  <td className="feed-table__td">{r.title}</td>
                  <td className="feed-table__td feed-table__td--link">
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
      )}
      {footer ? <div className="feed-board__footer">{footer}</div> : null}
    </section>
  )
}
