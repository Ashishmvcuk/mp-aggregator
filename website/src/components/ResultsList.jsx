import { ResultTableRow } from './ResultTableRow'
import './ResultsList.css'

/**
 * @param {{ results: Array<{ university: string; title: string; result_url: string; date: string }>; emptyMessage?: string }} props
 */
export function ResultsList({ results, emptyMessage = 'No results match your search.' }) {
  return (
    <section className="results-board" aria-labelledby="results-heading" id="latest-results">
      <h2 id="results-heading" className="results-board__title">
        Latest MP university results
      </h2>
      <p className="results-board__note">
        All links open the official university portal in a new tab. Verify marks and notifications only on the
        university website.
      </p>

      {results.length === 0 ? (
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
      )}
    </section>
  )
}
