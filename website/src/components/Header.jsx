import { Link } from 'react-router-dom'
import { useScrapeMeta } from '../context/ScrapeMetaContext'
import { formatScrapedAtUtc } from '../utils/scrapeMetaFormat'
import { SectionNavLink } from './SectionNavLink'
import './Header.css'

export function Header() {
  const { meta, loading } = useScrapeMeta()
  const lastRunLabel = meta?.scrapedAt ? formatScrapedAtUtc(meta.scrapedAt) : null

  return (
    <header className="sr-header">
      <div className="sr-header__brand-band">
        <div className="sr-header__inner">
          <Link className="sr-header__logo" to="/">
            MP UNIVERSITY RESULTS <span className="sr-header__reg">®</span>
          </Link>
          <p className="sr-header__tagline">
            MP University Result {new Date().getFullYear()} — Official style dashboard for Madhya Pradesh
            university examination links
          </p>
          <p className="sr-header__last-run" role="status">
            {loading ? (
              <span className="sr-header__last-run-muted">Checking last scraper run…</span>
            ) : lastRunLabel ? (
              <>
                Last scraper run:{' '}
                <time className="sr-header__last-run-time" dateTime={String(meta.scrapedAt)}>
                  {lastRunLabel}
                </time>
              </>
            ) : (
              <span className="sr-header__last-run-muted">Last scraper run: not available</span>
            )}
          </p>
        </div>
      </div>
      <div className="sr-header__accent" aria-hidden />
      <nav className="sr-header__nav" aria-label="Primary">
        <div className="sr-header__inner sr-header__nav-inner">
          <ul className="sr-header__menu">
            <li>
              <Link to="/" className="sr-header__nav-link">
                Home
              </Link>
            </li>
            <li>
              <SectionNavLink hashId="latest-results" className="sr-header__nav-link">
                Latest Results
              </SectionNavLink>
            </li>
            <li>
              <SectionNavLink hashId="latest-news" className="sr-header__nav-link">
                News
              </SectionNavLink>
            </li>
            <li>
              <SectionNavLink hashId="landing-jobs" className="sr-header__nav-link">
                Jobs
              </SectionNavLink>
            </li>
            <li>
              <SectionNavLink hashId="landing-admit" className="sr-header__nav-link">
                Admit cards
              </SectionNavLink>
            </li>
            <li>
              <SectionNavLink hashId="landing-syllabus" className="sr-header__nav-link">
                Syllabus
              </SectionNavLink>
            </li>
            <li>
              <Link to="/admit-cards" className="sr-header__nav-link">
                All admits
              </Link>
            </li>
            <li>
              <SectionNavLink hashId="universities" className="sr-header__nav-link">
                Universities
              </SectionNavLink>
            </li>
            <li>
              <SectionNavLink hashId="dashboard" className="sr-header__nav-link">
                Dashboard
              </SectionNavLink>
            </li>
          </ul>
        </div>
      </nav>
    </header>
  )
}
