import { formatDateMedium } from '../utils/formatDate'
import './SummaryCards.css'

/**
 * @param {{ universityCount: number; resultCount: number; latestDate: string | null }} summary
 */
export function SummaryCards({ summary }) {
  const cards = [
    { label: 'Universities on file', value: String(summary.universityCount) },
    { label: 'Total result links', value: String(summary.resultCount) },
    { label: 'Latest update', value: formatDateMedium(summary.latestDate) },
  ]

  return (
    <section className="sr-summary" aria-label="Summary statistics" id="universities">
      <h2 className="sr-summary__heading">Important information</h2>
      <ul className="sr-summary__list">
        {cards.map((c) => (
          <li key={c.label} className="sr-summary__item">
            <p className="sr-summary__value">{c.value}</p>
            <p className="sr-summary__label">{c.label}</p>
          </li>
        ))}
      </ul>
    </section>
  )
}
