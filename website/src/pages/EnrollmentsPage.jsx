import { useState } from 'react'
import { Link } from 'react-router-dom'
import { FeedList } from '../components/FeedList'
import { Footer } from '../components/Footer'
import { Header } from '../components/Header'
import { SearchBar } from '../components/SearchBar'
import { useEnrollments } from '../hooks/useEnrollments'
import './ListingPage.css'

export function EnrollmentsPage() {
  const [query, setQuery] = useState('')
  const { filtered, loading, error, titleSuggestions } = useEnrollments(query)

  return (
    <div className="listing-page">
      <Header />
      <main className="listing-page__main">
        <div className="listing-page__container">
          <nav className="listing-page__crumb" aria-label="Breadcrumb">
            <Link to="/">Dashboard</Link>
            <span aria-hidden> / </span>
            <span>Enrollments & admissions</span>
          </nav>

          <h1 className="listing-page__h1">Enrollment & admissions</h1>

          <SearchBar
            id="enrollments-search"
            label="Search by university or title"
            value={query}
            onChange={setQuery}
            placeholder="Search by university or title…"
            disabled={loading || !!error}
            titleSuggestions={titleSuggestions}
          />

          {error && (
            <div className="listing-page__banner listing-page__banner--error" role="alert">
              {error}
            </div>
          )}

          {loading ? (
            <p className="listing-page__loading" role="status">
              Loading enrollments…
            </p>
          ) : (
            <FeedList
              id="enrollments-list"
              title="All enrollment & admission links"
              items={filtered}
              emptyMessage="No enrollments match your search, or none have been scraped yet — run the scraper and sync enrollments.json."
              disableMobileCollapse
              pageSize={20}
              paginated
            />
          )}
        </div>
      </main>
      <Footer />
    </div>
  )
}
