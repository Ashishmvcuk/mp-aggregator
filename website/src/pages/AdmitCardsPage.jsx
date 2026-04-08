import { useState } from 'react'
import { Link } from 'react-router-dom'
import { FeedList } from '../components/FeedList'
import { Footer } from '../components/Footer'
import { Header } from '../components/Header'
import { SearchBar } from '../components/SearchBar'
import { useAdmitCards } from '../hooks/useAdmitCards'
import './AdmitCardsPage.css'

export function AdmitCardsPage() {
  const [query, setQuery] = useState('')
  const { filtered, loading, error, universityNames, titleSuggestions } = useAdmitCards(query)

  return (
    <div className="admit-page">
      <Header />
      <main className="admit-page__main">
        <div className="admit-page__container">
          <nav className="admit-page__crumb" aria-label="Breadcrumb">
            <Link to="/">Dashboard</Link>
            <span aria-hidden> / </span>
            <span>Admit cards</span>
          </nav>

          <h1 className="admit-page__h1">Admit cards & hall tickets</h1>
          <p className="admit-page__lead">
            Aggregated links from configured MP university portals. Always confirm details on the official site.
          </p>

          <SearchBar
            id="admit-search"
            label="Search admit cards by university or title"
            value={query}
            onChange={setQuery}
            placeholder="Search by university or title…"
            disabled={loading || !!error}
            universityNames={universityNames}
            titleSuggestions={titleSuggestions}
          />

          {error && (
            <div className="admit-page__banner admit-page__banner--error" role="alert">
              {error}
            </div>
          )}

          {loading ? (
            <p className="admit-page__loading" role="status">
              Loading admit cards…
            </p>
          ) : (
            <FeedList
              id="admit-cards-list"
              title="All admit cards"
              items={filtered}
              emptyMessage="No admit cards match your search, or none have been scraped yet."
            />
          )}
        </div>
      </main>
      <Footer />
    </div>
  )
}
