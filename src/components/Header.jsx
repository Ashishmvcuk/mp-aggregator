import './Header.css'

const nav = [
  { label: 'Home', href: '#' },
  { label: 'Latest Results', href: '#latest-results' },
  { label: 'Universities', href: '#universities' },
  { label: 'Dashboard', href: '#dashboard' },
]

export function Header() {
  return (
    <header className="sr-header">
      <div className="sr-header__brand-band">
        <div className="sr-header__inner">
          <a className="sr-header__logo" href="#">
            MP UNIVERSITY RESULTS <span className="sr-header__reg">®</span>
          </a>
          <p className="sr-header__tagline">
            MP University Result {new Date().getFullYear()} — Official style dashboard for Madhya Pradesh
            university examination links
          </p>
        </div>
      </div>
      <div className="sr-header__accent" aria-hidden />
      <nav className="sr-header__nav" aria-label="Primary">
        <div className="sr-header__inner sr-header__nav-inner">
          <ul className="sr-header__menu">
            {nav.map((item) => (
              <li key={item.label}>
                <a href={item.href} className="sr-header__nav-link">
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </nav>
    </header>
  )
}
