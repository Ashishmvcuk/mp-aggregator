import { formatDateShort } from '../utils/formatDate'

/**
 * @param {{ result: { university: string; title: string; result_url: string; date: string; officialReferenceMatch?: boolean }; index: number }} props
 */
export function ResultTableRow({ result, index }) {
  return (
    <tr className={index % 2 === 0 ? 'results-table__row results-table__row--even' : 'results-table__row'}>
      <td className="results-table__cell results-table__cell--date" data-label="Date">
        {formatDateShort(result.date)}
      </td>
      <td className="results-table__cell results-table__cell--uni" data-label="University">
        <div className="results-table__cell-wrap">
          {result.university}
          {result.officialReferenceMatch && (
            <span className="results-table__badge" title="University + URL host matches official reference">
              Official reference match
            </span>
          )}
        </div>
      </td>
      <td className="results-table__cell results-table__cell--title" data-label="Examination / result">
        <div className="results-table__cell-wrap">{result.title}</div>
      </td>
      <td className="results-table__cell results-table__cell--link" data-label="Link">
        <a
          className="results-table__link"
          href={result.result_url}
          target="_blank"
          rel="noopener noreferrer"
        >
          Click Here
        </a>
      </td>
    </tr>
  )
}
