import { HashRouter, Route, Routes } from 'react-router-dom'
import { VersionStamp } from './components/VersionStamp'
import { AdmitCardsPage } from './pages/AdmitCardsPage'
import { HomePage } from './pages/HomePage'

function App() {
  return (
    <HashRouter>
      <VersionStamp />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/admit-cards" element={<AdmitCardsPage />} />
      </Routes>
    </HashRouter>
  )
}

export default App
