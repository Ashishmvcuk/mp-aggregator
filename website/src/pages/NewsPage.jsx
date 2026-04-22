import { useState } from 'react'
import { Link } from 'react-router-dom'
import { FeedList } from '../components/FeedList'
import { Footer } from '../components/Footer'
import { Header } from '../components/Header'
import { SearchBar } from '../components/SearchBar'
import { useNews } from '../hooks/useNews'
import './ListingPage.css'

export function NewsPage() {
  const [query, setQuery] = useState('')
  const { filtered, loading, error, universityNames, titleSuggestions } = useNews(query)

  return (
    <div className="listing-page">
      <Header />
      <main className="listing-page__main">
        <div className="listing-page__container">
          <nav className="listing-page__crumb" aria-label="Breadcrumb">
            <Link to="/">Dashboard</Link>
            <span aria-hidden> / </span>
            <span>News & notices</span>
          </nav>

          <h1 className="listing-page__h1">Latest news & notices</h1>
          <p className="listing-page__lead">
            Aggregated notices from configured MP university portals. Always confirm details on the official site.
          </p>

          <SearchBar
            id="news-search"
            label="Search news by university or title"
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
              Loading news…
            </p>
          ) : (
            <FeedList
              id="news-list"
              title="All news & notices"
              items={filtered}
              emptyMessage="No news matches your search, or none are on file yet."
              showAnnouncedDate={false}
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
