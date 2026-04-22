import { useState } from 'react'
import { Link } from 'react-router-dom'
import { FeedList } from '../components/FeedList'
import { Footer } from '../components/Footer'
import { Header } from '../components/Header'
import { SearchBar } from '../components/SearchBar'
import { useSyllabus } from '../hooks/useSyllabus'
import './ListingPage.css'

export function SyllabusPage() {
  const [query, setQuery] = useState('')
  const { filtered, loading, error, universityNames, titleSuggestions } = useSyllabus(query)

  return (
    <div className="listing-page">
      <Header />
      <main className="listing-page__main">
        <div className="listing-page__container">
          <nav className="listing-page__crumb" aria-label="Breadcrumb">
            <Link to="/">Dashboard</Link>
            <span aria-hidden> / </span>
            <span>Syllabus & schemes</span>
          </nav>

          <h1 className="listing-page__h1">Syllabus & schemes</h1>
          <p className="listing-page__lead">
            Aggregated syllabus and scheme links from configured MP university portals. Always confirm details on the official site.
          </p>

          <SearchBar
            id="syllabus-search"
            label="Search syllabus by university or title"
            value={query}
            onChange={setQuery}
            placeholder="Search by university or title…"
            disabled={loading || !!error}
            universityNames={universityNames}
            titleSuggestions={titleSuggestions}
          />

          {error && (
            <div className="listing-page__banner listing-page__banner--error" role="alert">
              {error}
            </div>
          )}

          {loading ? (
            <p className="listing-page__loading" role="status">
              Loading syllabus…
            </p>
          ) : (
            <FeedList
              id="syllabus-list"
              title="All syllabus & schemes"
              items={filtered}
              emptyMessage="No syllabus entries match your search, or none are on file yet."
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
