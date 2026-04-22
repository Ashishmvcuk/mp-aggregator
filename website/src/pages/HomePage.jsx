import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { DashboardChart } from '../components/DashboardChart'
import { FeedList } from '../components/FeedList'
import { Footer } from '../components/Footer'
import { Header } from '../components/Header'
import { ResultsList } from '../components/ResultsList'
import { ResultsTicker } from '../components/ResultsTicker'
import { SearchBar } from '../components/SearchBar'
import { SectionNavLink } from '../components/SectionNavLink'
import { SidebarEnrollmentTable } from '../components/SidebarEnrollmentTable'
import { SidebarQuickLinks } from '../components/SidebarQuickLinks'
import { SidebarUniversitiesDirectory } from '../components/SidebarUniversitiesDirectory'
import { SummaryCards } from '../components/SummaryCards'
import { useDashboardFeeds } from '../hooks/useDashboardFeeds'
import { useResults } from '../hooks/useResults'
import './HomePage.css'

export function HomePage() {
  const [query, setQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [selectedUniversity, setSelectedUniversity] = useState('all')
  const feeds = useDashboardFeeds()
  const typeOptions = useMemo(() => {
    const s = new Set(feeds.universityPortals.map((p) => p.type).filter(Boolean))
    return [...s].sort((a, b) => a.localeCompare(b))
  }, [feeds.universityPortals])
  const universityOptions = useMemo(
    () => [...feeds.universityPortals].map((p) => p.university).sort((a, b) => a.localeCompare(b)),
    [feeds.universityPortals]
  )
  const { items, filtered, summary, loading, error, universityNames, titleSuggestions } = useResults(
    query,
    { typeFilter, selectedUniversity, referenceRows: feeds.universityPortals }
  )

  return (
    <div className="home-page">
      <Header />
      <ResultsTicker results={items} loading={loading} />
      <main className="home-page__main">
        <div className="home-page__container">
          <div className="home-page__layout">
            <div className="home-page__primary">
              <p className="home-page__intro">
                Quick jump:{' '}
                <SectionNavLink hashId="latest-news" className="home-page__intro-link">
                  Latest news
                </SectionNavLink>
                {' · '}
                <Link to="/enrollments" className="home-page__intro-link">
                  Admission Open
                </Link>
                {' · '}
                <SectionNavLink hashId="university-portals" className="home-page__intro-link">
                  University portals
                </SectionNavLink>
                {' · '}
                <SectionNavLink hashId="latest-results" className="home-page__intro-link">
                  Results
                </SectionNavLink>
                {' · '}
                <SectionNavLink hashId="landing-admit" className="home-page__intro-link">
                  Admit cards
                </SectionNavLink>
                {' · '}
                <SectionNavLink hashId="landing-syllabus" className="home-page__intro-link">
                  Syllabus
                </SectionNavLink>
                {' · '}
                <Link to="/admit-cards" className="home-page__intro-link">
                  Full admit list
                </Link>
              </p>

              {!feeds.loading && (typeOptions.length > 0 || universityOptions.length > 0) && (
                <div className="home-page__group-filter">
                  <label htmlFor="home-type-filter" className="home-page__group-filter-label">
                    University type
                  </label>
                  <select
                    id="home-type-filter"
                    className="home-page__group-filter-select"
                    value={typeFilter}
                    onChange={(e) => setTypeFilter(e.target.value)}
                  >
                    <option value="all">All types</option>
                    {typeOptions.map((t) => (
                      <option key={t} value={t}>
                        {t}
                      </option>
                    ))}
                  </select>
                  <label htmlFor="home-university-filter" className="home-page__group-filter-label">
                    University
                  </label>
                  <select
                    id="home-university-filter"
                    className="home-page__group-filter-select"
                    value={selectedUniversity}
                    onChange={(e) => setSelectedUniversity(e.target.value)}
                  >
                    <option value="all">All universities</option>
                    {universityOptions.map((u) => (
                      <option key={u} value={u}>
                        {u}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <SearchBar
                value={query}
                onChange={setQuery}
                disabled={loading || !!error}
                universityNames={universityNames}
                titleSuggestions={titleSuggestions}
              />

              {error && (
                <div className="home-page__banner home-page__banner--error" role="alert">
                  {error}
                </div>
              )}

              {feeds.error && (
                <div className="home-page__banner home-page__banner--error" role="alert">
                  {feeds.error}
                </div>
              )}

              {!feeds.loading && (
                <div className="home-page__enroll-mobile">
                  <SidebarEnrollmentTable
                    items={feeds.enrollmentsPreview}
                    totalCount={feeds.enrollmentsTotal}
                    placement="mobile"
                  />
                  <SidebarUniversitiesDirectory
                    portals={feeds.universityPortals}
                    filterQuery={query}
                    selectedUniversity={selectedUniversity}
                    typeFilter={typeFilter}
                  />
                </div>
              )}

              {loading ? (
                <p className="home-page__loading" role="status">
                  Loading latest results…
                </p>
              ) : (
                <>
                  <SummaryCards summary={summary} />
                  <ResultsList
                    results={filtered}
                    emptyMessage="No results with an announced date match your search or filters."
                  />
                </>
              )}

              {feeds.loading ? (
                <p className="home-page__loading home-page__loading--secondary" role="status">
                  Loading news, enrollments, syllabus, and admit cards…
                </p>
              ) : (
                <FeedList
                  id="latest-news"
                  title="Latest news & notices"
                  subtitle="From the last 30 days. Official university links only."
                  items={feeds.newsLast30Days}
                  emptyMessage="No news loaded — run the scraper and sync to website/public/data/ (see README)."
                  showAnnouncedDate={false}
                />
              )}

              {!feeds.loading && (
                <>
                  <FeedList
                    id="landing-admit"
                    title="Admit cards & hall tickets"
                    subtitle={
                      feeds.admitCardsTotal > feeds.admitCardsHomePreview.length
                        ? `Showing ${feeds.admitCardsHomePreview.length} of ${feeds.admitCardsTotal} on file.`
                        : undefined
                    }
                    items={feeds.admitCardsHomePreview}
                    emptyMessage="No admit cards with an announced date on file yet — run the scraper and sync, or confirm dates on the source sites."
                    footer={
                      <Link to="/admit-cards">Open full admit cards page →</Link>
                    }
                  />
                  <FeedList
                    id="landing-syllabus"
                    title="Syllabus & schemes"
                    items={feeds.syllabusSorted}
                    emptyMessage="No syllabus links in data yet — sync scraper output to website/public/data/syllabus.json."
                  />
                  <FeedList
                    id="blogs"
                    title="Blogs & articles"
                    items={feeds.blogsSorted}
                    emptyMessage="No blog links with an announced date on file yet — run the scraper and sync, or confirm dates on the source sites."
                  />
                </>
              )}

              {!loading && <DashboardChart items={items} />}
            </div>
            <div className="home-page__sidebar-col">
              <SidebarQuickLinks onPick={setQuery} />
              {!feeds.loading && (
                <div className="home-page__enroll-desktop">
                  <SidebarEnrollmentTable
                    items={feeds.enrollmentsPreview}
                    totalCount={feeds.enrollmentsTotal}
                    placement="sidebar"
                  />
                  <SidebarUniversitiesDirectory
                    portals={feeds.universityPortals}
                    filterQuery={query}
                    selectedUniversity={selectedUniversity}
                    typeFilter={typeFilter}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
