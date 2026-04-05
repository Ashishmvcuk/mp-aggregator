import './SearchBar.css'

/**
 * @param {{ value: string; onChange: (v: string) => void; disabled?: boolean }} props
 */
export function SearchBar({ value, onChange, disabled }) {
  return (
    <div className="sr-search">
      <label className="sr-search__label" htmlFor="results-search">
        Search by university name or result title
      </label>
      <div className="sr-search__row">
        <input
          id="results-search"
          type="search"
          className="sr-search__input"
          placeholder="Type here to filter the table below…"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          autoComplete="off"
        />
        <span className="sr-search__hint">Live filter</span>
      </div>
    </div>
  )
}
