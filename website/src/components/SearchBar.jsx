import { useMemo, useState } from 'react'
import './SearchBar.css'

/**
 * @param {{
 *   value: string
 *   onChange: (v: string) => void
 *   disabled?: boolean
 *   id?: string
 *   label?: string
 *   placeholder?: string
 *   universityNames?: string[]
 *   titleSuggestions?: string[]
 * }} props
 */
export function SearchBar({
  value,
  onChange,
  disabled,
  id = 'results-search',
  label = 'Search by university name or result title',
  placeholder = 'Type to filter results and match universities…',
  universityNames = [],
  titleSuggestions = [],
}) {
  const [open, setOpen] = useState(false)
  const q = value.trim().toLowerCase()

  const { uniMatches, titleMatches } = useMemo(() => {
    if (!q) {
      return { uniMatches: [], titleMatches: [] }
    }
    const uni = universityNames.filter((u) => u.toLowerCase().includes(q)).slice(0, 8)
    const titles = titleSuggestions.filter((t) => t.toLowerCase().includes(q)).slice(0, 8)
    return { uniMatches: uni, titleMatches: titles }
  }, [q, universityNames, titleSuggestions])

  const showPanel = open && !disabled && q.length >= 1 && (uniMatches.length > 0 || titleMatches.length > 0)

  const pick = (v) => {
    onChange(v)
    setOpen(false)
  }

  return (
    <div className="sr-search">
      <label className="sr-search__label" htmlFor={id}>
        {label}
      </label>
      <div className="sr-search__wrap">
        <div className="sr-search__row">
          <input
            id={id}
            type="search"
            className="sr-search__input"
            placeholder={placeholder}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onFocus={() => setOpen(true)}
            onBlur={() => setTimeout(() => setOpen(false), 180)}
            disabled={disabled}
            autoComplete="off"
            role="combobox"
            aria-expanded={showPanel}
            aria-controls={`${id}-suggestions`}
            aria-autocomplete="list"
          />
          <span className="sr-search__hint">Live filter · suggestions</span>
        </div>
        {showPanel && (
          <ul
            id={`${id}-suggestions`}
            className="sr-search__suggestions"
            role="listbox"
            aria-label="Search suggestions"
          >
            {uniMatches.length > 0 && (
              <li className="sr-search__suggestions-heading" role="presentation">
                Universities
              </li>
            )}
            {uniMatches.map((u) => (
              <li key={`u-${u}`} role="option">
                <button
                  type="button"
                  className="sr-search__suggestion-btn"
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => pick(u)}
                >
                  {u}
                </button>
              </li>
            ))}
            {titleMatches.length > 0 && (
              <li className="sr-search__suggestions-heading" role="presentation">
                Result titles
              </li>
            )}
            {titleMatches.map((t) => (
              <li key={`t-${t}`} role="option">
                <button
                  type="button"
                  className="sr-search__suggestion-btn"
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => pick(t)}
                >
                  {t.length > 120 ? `${t.slice(0, 117)}…` : t}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
