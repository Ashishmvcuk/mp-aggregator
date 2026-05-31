import './ImportantLinksList.css'

/**
 * @param {{
 *   items: Array<{ category: string; organization: string; websitelink: string; logo?: string }>
 *   emptyMessage?: string
 *   compact?: boolean
 * }} props
 */
export function ImportantLinksList({ items, emptyMessage = 'Nothing to show yet.', compact = false }) {
  if (items.length === 0) {
    return (
      <p className="imp-links__empty" role="status">
        {emptyMessage}
      </p>
    )
  }

  return (
    <div className={`imp-links${compact ? ' imp-links--compact' : ''}`}>
      <div className="imp-links__scroll">
        {compact ? (
          <table className="imp-links__table">
            <tbody>
              {items.map((row) => (
                <tr key={`${row.category}-${row.organization}-${row.websitelink}`}>
                  <td className="imp-links__cell">
                    <span className="imp-links__cat">{row.category}</span>
                    {row.logo ? (
                      <img
                        src={row.logo}
                        alt=""
                        className="imp-links__logo"
                        width="16"
                        height="16"
                        loading="lazy"
                        decoding="async"
                      />
                    ) : null}
                    <a
                      href={row.websitelink}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="imp-links__link"
                    >
                      {row.organization}
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <table className="imp-links__table">
            <thead>
              <tr>
                <th scope="col">Category</th>
                <th scope="col">Organization</th>
              </tr>
            </thead>
            <tbody>
              {items.map((row) => (
                <tr key={`${row.category}-${row.organization}-${row.websitelink}`}>
                  <td className="imp-links__cat">{row.category}</td>
                  <td className="imp-links__org">
                    {row.logo ? (
                      <img
                        src={row.logo}
                        alt=""
                        className="imp-links__logo"
                        width="20"
                        height="20"
                        loading="lazy"
                        decoding="async"
                      />
                    ) : null}
                    <a
                      href={row.websitelink}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="imp-links__link"
                    >
                      {row.organization}
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
