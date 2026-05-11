import { useEffect, useMemo, useState } from 'react'
import { MP_UNIVERSITY_NAMES } from '../constants/mpUniversityNames.js'
import './SearchBar.css'

const MAX_UNI_SUGGESTIONS_TYPED = 25
const LISTBOX_ID_SUFFIX = '-suggestions'

/**
 * @param {{
 *   value: string
 *   onChange: (v: string) => void
 *   disabled?: boolean
 *   id?: string
 *   label?: string
 *   placeholder?: string
 *   titleSuggestions?: string[]
 * }} props
 */
export function SearchBar({
  value,
  onChange,
  disabled,
  id = 'results-search',
  label = 'Search by university name or result title',
  placeholder = 'Type to search, or open the list to browse all MP universities…',
  titleSuggestions = [],
}) {
  const [open, setOpen] = useState(false)
  const q = value.trim().toLowerCase()

  const { uniMatches, titleMatches } = useMemo(() => {
    const allUni = [...MP_UNIVERSITY_NAMES]
    if (!q) {
      return { uniMatches: allUni, titleMatches: [] }
    }
    const uni = allUni.filter((u) => u.toLowerCase().includes(q)).slice(0, MAX_UNI_SUGGESTIONS_TYPED)
    const titles = titleSuggestions.filter((t) => t.toLowerCase().includes(q)).slice(0, 12)
    return { uniMatches: uni, titleMatches: titles }
  }, [q, titleSuggestions])

  const showPanel =
    open &&
    !disabled &&
    (uniMatches.length > 0 || titleMatches.length > 0)

  const pick = (v) => {
    onChange(v)
    setOpen(false)
  }

  useEffect(() => {
    if (!open) return undefined
    const onKey = (e) => {
      if (e.key === 'Escape') setOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open])

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
            onKeyDown={(e) => {
              if (e.key === 'ArrowDown' && !open) setOpen(true)
            }}
            disabled={disabled}
            autoComplete="off"
            role="combobox"
            aria-expanded={showPanel}
            aria-controls={`${id}${LISTBOX_ID_SUFFIX}`}
            aria-autocomplete="list"
          />
          <span className="sr-search__hint">
            {MP_UNIVERSITY_NAMES.length} universities · live filter
          </span>
        </div>
        {showPanel && (
          <ul
            id={`${id}${LISTBOX_ID_SUFFIX}`}
            className="sr-search__suggestions"
            role="listbox"
            aria-label="Search suggestions"
          >
            {uniMatches.length > 0 && (
              <li className="sr-search__suggestions-heading" role="presentation">
                {q ? 'Universities (matching)' : 'Universities'}
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
