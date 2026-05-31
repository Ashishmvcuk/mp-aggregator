import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Footer } from '../components/Footer'
import { Header } from '../components/Header'
import { ImportantLinksList } from '../components/ImportantLinksList'
import { Pagination } from '../components/Pagination'
import { SearchBar } from '../components/SearchBar'
import { useImportantLinks } from '../hooks/useImportantLinks'
import './ListingPage.css'

const PAGE_SIZE = 20

export function ImportantLinksPage() {
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const { filtered, loading, error, titleSuggestions } = useImportantLinks(query)

  useEffect(() => {
    setPage(1)
  }, [query])

  const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  const safePage = Math.min(page, pageCount)
  const pagedItems = useMemo(() => {
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
            <span>Important sections</span>
          </nav>

          <h1 className="listing-page__h1">Important sections</h1>
          <p className="listing-page__lead">
            Official links to national academic, government, and professional bodies. Always verify
            details on each organization&apos;s website.
          </p>

          <SearchBar
            id="important-links-search"
            label="Search by category or organization"
            value={query}
            onChange={setQuery}
            placeholder="Search by category or organization…"
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
              Loading important links…
            </p>
          ) : (
            <>
              <ImportantLinksList
                items={pagedItems}
                emptyMessage="No important links match your search."
              />
              <Pagination
                page={safePage}
                pageCount={pageCount}
                onChange={setPage}
                totalItems={filtered.length}
                pageSize={PAGE_SIZE}
                label="Important links pagination"
              />
            </>
          )}
        </div>
      </main>
      <Footer />
    </div>
  )
}
