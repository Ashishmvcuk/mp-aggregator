import './SearchBar.css'

/**
 * @param {{ value: string; onChange: (v: string) => void; disabled?: boolean; id?: string; label?: string; placeholder?: string }} props
 */
export function SearchBar({
  value,
  onChange,
  disabled,
  id = 'results-search',
  label = 'Search by university name or result title',
  placeholder = 'Type here to filter the table below…',
}) {
  return (
    <div className="sr-search">
      <label className="sr-search__label" htmlFor={id}>
        {label}
      </label>
      <div className="sr-search__row">
        <input
          id={id}
          type="search"
          className="sr-search__input"
          placeholder={placeholder}
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
