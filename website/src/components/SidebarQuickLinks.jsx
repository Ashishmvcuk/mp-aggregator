import './SidebarQuickLinks.css'

const LINKS = [
  { label: 'Barkatullah University', term: 'Barkatullah' },
  { label: 'RGPV', term: 'RGPV' },
  { label: 'Raja Shankar Shah University, Chhindwara', term: 'Raja Shankar Shah' },
  { label: 'DAVV', term: 'DAVV' },
  { label: 'Rani Durgavati Vishwavidyalaya', term: 'Rani Durgavati' },
  { label: 'Jiwaji University', term: 'Jiwaji' },
  { label: 'APSU', term: 'APSU' },
  { label: 'Vikram University', term: 'Vikram' },
]

/**
 * @param {{ onPick: (term: string) => void }} props
 */
export function SidebarQuickLinks({ onPick }) {
  return (
    <aside className="sr-sidebar" aria-label="Quick university filters" id="universities">
      <h2 className="sr-sidebar__title">Popular universities</h2>
      <p className="sr-sidebar__text">Tap a name to filter the main table.</p>
      <ul className="sr-sidebar__list">
        {LINKS.map((l) => (
          <li key={l.term}>
            <button type="button" className="sr-sidebar__btn" onClick={() => onPick(l.term)}>
              {l.label}
            </button>
          </li>
        ))}
      </ul>
    </aside>
  )
}
