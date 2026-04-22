import { HashRouter, Route, Routes } from 'react-router-dom'
import { VersionStamp } from './components/VersionStamp'
import { ScrapeMetaProvider } from './context/ScrapeMetaContext'
import { AdminPage } from './pages/AdminPage'
import { AdmitCardsPage } from './pages/AdmitCardsPage'
import { EnrollmentsPage } from './pages/EnrollmentsPage'
import { HomePage } from './pages/HomePage'
import { NewsPage } from './pages/NewsPage'
import { ResultsPage } from './pages/ResultsPage'
import { SyllabusPage } from './pages/SyllabusPage'

function App() {
  return (
    <HashRouter>
      <ScrapeMetaProvider>
        <VersionStamp />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/admit-cards" element={<AdmitCardsPage />} />
          <Route path="/news" element={<NewsPage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/syllabus" element={<SyllabusPage />} />
          <Route path="/enrollments" element={<EnrollmentsPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </ScrapeMetaProvider>
    </HashRouter>
  )
}

export default App
