import { lazy, Suspense } from 'react'
import { HashRouter, Route, Routes } from 'react-router-dom'
import { VersionStamp } from './components/VersionStamp'
import { ScrapeMetaProvider } from './context/ScrapeMetaContext'
import { AdmitCardsPage } from './pages/AdmitCardsPage'
import { HomePage } from './pages/HomePage'

const AdminPage = lazy(() => import('./pages/AdminPage'))

function App() {
  return (
    <HashRouter>
      <ScrapeMetaProvider>
        <VersionStamp />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/admit-cards" element={<AdmitCardsPage />} />
          <Route
            path="/admin"
            element={
              <Suspense
                fallback={
                  <div style={{ padding: '2rem', textAlign: 'center', fontFamily: 'system-ui' }}>
                    Loading admin…
                  </div>
                }
              >
                <AdminPage />
              </Suspense>
            }
          />
        </Routes>
      </ScrapeMetaProvider>
    </HashRouter>
  )
}

export default App
