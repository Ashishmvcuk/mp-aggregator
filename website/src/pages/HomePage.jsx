import { useState } from 'react'
import { DashboardChart } from '../components/DashboardChart'
import { Footer } from '../components/Footer'
import { Header } from '../components/Header'
import { ResultsList } from '../components/ResultsList'
import { SearchBar } from '../components/SearchBar'
import { SidebarQuickLinks } from '../components/SidebarQuickLinks'
import { SummaryCards } from '../components/SummaryCards'
import { useResults } from '../hooks/useResults'
import './HomePage.css'

export function HomePage() {
  const [query, setQuery] = useState('')
  const { items, filtered, summary, loading, error } = useResults(query)

  return (
    <div className="home-page">
      <Header />
      <main className="home-page__main">
        <div className="home-page__container">
          <div className="home-page__layout">
            <div className="home-page__primary">
              <SearchBar value={query} onChange={setQuery} disabled={loading || !!error} />

              {error && (
                <div className="home-page__banner home-page__banner--error" role="alert">
                  {error}
                </div>
              )}

              {loading ? (
                <p className="home-page__loading" role="status">
                  Loading latest results…
                </p>
              ) : (
                <>
                  <SummaryCards summary={summary} />
                  <ResultsList results={filtered} />
                  <DashboardChart items={items} />
                </>
              )}
            </div>
            <SidebarQuickLinks onPick={setQuery} />
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
