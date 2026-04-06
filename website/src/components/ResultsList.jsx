import { ResultTableRow } from './ResultTableRow'
import { useIsMobileLayout } from '../hooks/useIsMobileLayout'
import './ResultsList.css'
import './MobileCollapsibleTable.css'

const RESULTS_TITLE = 'Latest MP university results'

/**
 * @param {{ results: Array<{ university: string; title: string; result_url: string; date: string }>; emptyMessage?: string }} props
 */
export function ResultsList({ results, emptyMessage = 'No results match your search.' }) {
  const mobile = useIsMobileLayout()
  const hasItems = results.length > 0

  const tableBlock =
    results.length === 0 ? (
      <p className="results-board__empty" role="status">
        {emptyMessage}
      </p>
    ) : (
      <div className="results-board__scroll">
        <table className="results-table">
          <colgroup>
            <col className="results-table__col results-table__col--date" />
            <col className="results-table__col results-table__col--uni" />
            <col className="results-table__col results-table__col--title" />
            <col className="results-table__col results-table__col--link" />
          </colgroup>
          <thead>
            <tr>
              <th scope="col" className="results-table__th results-table__th--date">
                Date
              </th>
              <th scope="col" className="results-table__th results-table__th--uni">
                University
              </th>
              <th scope="col" className="results-table__th results-table__th--title">
                Examination / result
              </th>
              <th scope="col" className="results-table__th results-table__th--link">
                Link
              </th>
            </tr>
          </thead>
          <tbody>
            {results.map((r, i) => (
              <ResultTableRow key={`${r.university}-${r.title}-${r.date}-${i}`} result={r} index={i} />
            ))}
          </tbody>
        </table>
      </div>
    )

  if (mobile) {
    const rowWord = results.length === 1 ? 'row' : 'rows'
    return (
      <section
        className="results-board results-board--mobile-collapse"
        aria-labelledby="results-heading"
        id="latest-results"
      >
        <details className="table-collapse">
          <summary className="table-collapse__summary">
            <span className="table-collapse__summary-title" id="results-heading">
              {RESULTS_TITLE}
            </span>
            <span className="table-collapse__summary-meta">
              {hasItems ? `Tap to show ${results.length} ${rowWord}` : 'Tap to open — no matches'}
            </span>
          </summary>
          <div className="table-collapse__inner">
            {tableBlock}
          </div>
        </details>
      </section>
    )
  }

  return (
    <section className="results-board" aria-labelledby="results-heading" id="latest-results">
      <h2 id="results-heading" className="results-board__title">
        {RESULTS_TITLE}
      </h2>
      {tableBlock}
    </section>
  )
}
