import { formatDateShort } from '../utils/formatDate'

/**
 * @param {{ result: { university: string; title: string; result_url: string; date: string }; index: number }} props
 */
export function ResultTableRow({ result, index }) {
  return (
    <tr className={index % 2 === 0 ? 'results-table__row results-table__row--even' : 'results-table__row'}>
      <td className="results-table__cell results-table__cell--date">{formatDateShort(result.date)}</td>
      <td className="results-table__cell results-table__cell--uni">
        <span className="results-table__uni">{result.university}</span>
      </td>
      <td className="results-table__cell results-table__cell--title">{result.title}</td>
      <td className="results-table__cell results-table__cell--link">
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
