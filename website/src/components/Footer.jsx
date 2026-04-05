import { Link } from 'react-router-dom'
import './Footer.css'

export function Footer() {
  return (
    <footer className="sr-footer">
      <div className="sr-footer__inner">
        <p className="sr-footer__admin-link">
          <Link to="/admin">Content admin</Link>
        </p>
        <div className="sr-footer__strip">
          <span className="sr-footer__badge">Disclaimer</span>
          <p className="sr-footer__text">
            This website only lists links to <strong>official university websites</strong>. MP University Results does
            not publish marksheets or conduct examinations. Always cross-check results, notices, and revaluation rules
            on the concerned university portal.
          </p>
        </div>
        <p className="sr-footer__copy">
          © {new Date().getFullYear()} MP University Results — For educational use. Not affiliated with any government
          body or third-party result portal.
        </p>
      </div>
    </footer>
  )
}
