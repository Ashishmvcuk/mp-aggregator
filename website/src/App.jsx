import { HashRouter, Route, Routes } from 'react-router-dom'
import { VersionStamp } from './components/VersionStamp'
import { ScrapeMetaProvider } from './context/ScrapeMetaContext'
import { AdminPage } from './pages/AdminPage'
import { AdmitCardsPage } from './pages/AdmitCardsPage'
import { HomePage } from './pages/HomePage'

function App() {
  return (
    <HashRouter>
      <ScrapeMetaProvider>
        <VersionStamp />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/admit-cards" element={<AdmitCardsPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </ScrapeMetaProvider>
    </HashRouter>
  )
}

export default App
