import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Footer } from '../components/Footer'
import { Header } from '../components/Header'
import { Pagination } from '../components/Pagination'
import { ResultsList } from '../components/ResultsList'
import { SearchBar } from '../components/SearchBar'
import { useResults } from '../hooks/useResults'
import './ListingPage.css'

const PAGE_SIZE = 20

export function ResultsPage() {
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const { filtered, loading, error, universityNames, titleSuggestions } = useResults(query)

  useEffect(() => {
    setPage(1)
  }, [filtered])

  const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  const safePage = Math.min(page, pageCount)
  const pagedResults = useMemo(() => {
    const start = (safePage - 1) * PAGE_SIZE
    return filtered.slice(start, start + PAGE_SIZE)
  }, [filtered, safePage])

  return (
    <div className="listing-page">
      <Header />
      <main className="listing-page__main">
        <div className="listing-page__container">
          <nav className="listing-page__crumb" aria-label="Breadcrumb">
            <Link to="/">Dashboard</Link>
            <span aria-hidden> / </span>
            <span>Results</span>
          </nav>

          <h1 className="listing-page__h1">Latest MP university results</h1>
          <p className="listing-page__lead">
            Aggregated result announcements from configured MP university portals. Always confirm marks on the official site.
          </p>

          <SearchBar
            id="results-search"
            label="Search results by university or title"
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
              Loading results…
            </p>
          ) : (
            <>
              <ResultsList
                results={pagedResults}
                emptyMessage="No results with an announced date match your search, or none are on file yet."
              />
              <Pagination
                page={safePage}
                pageCount={pageCount}
                onChange={setPage}
                totalItems={filtered.length}
                pageSize={PAGE_SIZE}
                label="Results pagination"
              />
            </>
          )}
        </div>
      </main>
      <Footer />
    </div>
  )
}
