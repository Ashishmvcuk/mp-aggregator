import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Footer } from '../components/Footer'
import { Header } from '../components/Header'
import { getSupabase } from '../lib/supabaseClient'
import {
  MANUAL_CATEGORIES,
  resetManualEntriesCache,
  supabaseRowToItem,
} from '../services/manualEntriesService'
import {
  closeAdminGate,
  isAdminGateOpen,
  tryAdminGateLogin,
} from '../utils/adminGate'
import './AdminPage.css'

const defaultForm = () => ({
  category: 'news',
  university: '',
  title: '',
  link_url: '',
  date: new Date().toISOString().slice(0, 10),
})

export function AdminPage() {
  const [gateOpen, setGateOpen] = useState(() => isAdminGateOpen())
  const [gateUser, setGateUser] = useState('')
  const [gatePass, setGatePass] = useState('')
  const [gateError, setGateError] = useState(null)

  const [supabaseSession, setSupabaseSession] = useState(null)
  const [email, setEmail] = useState('')
  const [supabasePassword, setSupabasePassword] = useState('')
  const [authError, setAuthError] = useState(null)
  const [busy, setBusy] = useState(false)
  const [form, setForm] = useState(defaultForm)
  const [rows, setRows] = useState([])
  const [listError, setListError] = useState(null)
  const [formMessage, setFormMessage] = useState(null)

  const sb = getSupabase()

  const refreshList = useCallback(async () => {
    if (!sb || !supabaseSession) return
    setListError(null)
    const { data, error } = await sb.from('manual_entries').select('*').order('created_at', { ascending: false })
    if (error) {
      setListError(error.message)
      return
    }
    setRows(data || [])
  }, [sb, supabaseSession])

  useEffect(() => {
    if (!sb) return undefined
    let cancelled = false
    sb.auth
      .getSession()
      .then(({ data }) => {
        if (!cancelled) setSupabaseSession(data.session ?? null)
      })
      .catch((err) => {
        console.error('[admin] getSession failed:', err)
        if (!cancelled) setSupabaseSession(null)
      })

    const { data } = sb.auth.onAuthStateChange((_event, session) => {
      setSupabaseSession(session ?? null)
    })
    const sub = data?.subscription
    return () => {
      cancelled = true
      try {
        sub?.unsubscribe()
      } catch {
        /* ignore */
      }
    }
  }, [sb])

  useEffect(() => {
    if (supabaseSession) void refreshList()
  }, [supabaseSession, refreshList])

  function handleGateLogin(e) {
    e.preventDefault()
    setGateError(null)
    if (tryAdminGateLogin(gateUser.trim(), gatePass)) {
      setGateOpen(true)
      setGatePass('')
    } else {
      setGateError('Invalid username or password.')
    }
  }

  function handleGateSignOut() {
    closeAdminGate()
    setGateOpen(false)
    setGateUser('')
    setGatePass('')
    if (sb) void sb.auth.signOut()
    setSupabaseSession(null)
    setRows([])
  }

  async function handleSupabaseSignIn(e) {
    e.preventDefault()
    if (!sb) return
    setAuthError(null)
    setBusy(true)
    const { error } = await sb.auth.signInWithPassword({ email: email.trim(), password: supabasePassword })
    setBusy(false)
    if (error) setAuthError(error.message)
  }

  async function handleSupabaseSignOut() {
    if (!sb) return
    await sb.auth.signOut()
    setRows([])
  }

  async function handleAdd(e) {
    e.preventDefault()
    if (!sb || !supabaseSession) return
    setFormMessage(null)
    const { category, university, title, link_url, date } = form
    if (!university.trim() || !title.trim() || !link_url.trim()) {
      setFormMessage('University, title, and link URL are required.')
      return
    }
    setBusy(true)
    const { error } = await sb.from('manual_entries').insert({
      category,
      university: university.trim(),
      title: title.trim(),
      link_url: link_url.trim(),
      date: date.trim() || new Date().toISOString().slice(0, 10),
    })
    setBusy(false)
    if (error) {
      setFormMessage(error.message)
      return
    }
    resetManualEntriesCache()
    setForm(defaultForm())
    setFormMessage('Saved. Visitors may need to refresh the site to see new rows.')
    await refreshList()
  }

  async function handleDelete(id) {
    if (!sb || !supabaseSession || !id) return
    if (!window.confirm('Remove this manual entry from the live site?')) return
    setBusy(true)
    const { error } = await sb.from('manual_entries').delete().eq('id', id)
    setBusy(false)
    if (error) {
      setListError(error.message)
      return
    }
    resetManualEntriesCache()
    await refreshList()
  }

  return (
    <div className="admin-page">
      <Header />
      <main className="admin-page__main">
        <div className="admin-page__container">
          <nav className="admin-page__crumb" aria-label="Breadcrumb">
            <Link to="/">Home</Link>
            <span aria-hidden> / </span>
            <span>Admin</span>
          </nav>

          <h1 className="admin-page__h1">Content admin</h1>
          <p className="admin-page__lead">
            Add links that appear alongside scraped data. Duplicate URLs are hidden in favor of manual entries.
          </p>

          {!gateOpen ? (
            <section className="admin-page__panel" aria-labelledby="admin-gate-h">
              <h2 id="admin-gate-h">Login</h2>
              <p className="admin-page__muted">Sign in to open the admin area.</p>
              <form className="admin-page__form" onSubmit={handleGateLogin}>
                <label className="admin-page__field">
                  <span>Username</span>
                  <input
                    autoComplete="username"
                    value={gateUser}
                    onChange={(e) => setGateUser(e.target.value)}
                    required
                  />
                </label>
                <label className="admin-page__field">
                  <span>Password</span>
                  <input
                    type="password"
                    autoComplete="current-password"
                    value={gatePass}
                    onChange={(e) => setGatePass(e.target.value)}
                    required
                  />
                </label>
                {gateError ? (
                  <p className="admin-page__error" role="alert">
                    {gateError}
                  </p>
                ) : null}
                <button type="submit" className="admin-page__btn">
                  Log in
                </button>
              </form>
            </section>
          ) : !sb ? (
            <>
              <section className="admin-page__panel admin-page__panel--toolbar">
                <p className="admin-page__signed">
                  Signed in as <strong>admin</strong>
                </p>
                <button type="button" className="admin-page__btn admin-page__btn--ghost" onClick={handleGateSignOut}>
                  Sign out
                </button>
              </section>
              <section className="admin-page__panel admin-page__panel--note" aria-labelledby="admin-setup-h">
                <h2 id="admin-setup-h">Supabase not configured</h2>
                <p>
                  To let editors add rows without editing Git, create a free{' '}
                  <a href="https://supabase.com" target="_blank" rel="noreferrer">
                    Supabase
                  </a>{' '}
                  project, run the SQL in <code>docs/supabase-manual-entries.sql</code>, create an auth user, then set
                  repository secrets <code>VITE_SUPABASE_URL</code> and <code>VITE_SUPABASE_ANON_KEY</code> and rebuild the
                  site.
                </p>
                <p>
                  Until then, commit edits to{' '}
                  <code>website/public/data/manual_additions.json</code> (same shape as scraped JSON per category).
                </p>
              </section>
            </>
          ) : !supabaseSession ? (
            <>
              <section className="admin-page__panel admin-page__panel--toolbar">
                <p className="admin-page__signed">
                  App login: <strong>admin</strong>
                </p>
                <button type="button" className="admin-page__btn admin-page__btn--ghost" onClick={handleGateSignOut}>
                  Sign out
                </button>
              </section>
              <section className="admin-page__panel" aria-labelledby="admin-login-h">
                <h2 id="admin-login-h">Database sign-in</h2>
                <p className="admin-page__muted">Use the Supabase Auth user you created for this project.</p>
                <form className="admin-page__form" onSubmit={handleSupabaseSignIn}>
                  <label className="admin-page__field">
                    <span>Email</span>
                    <input
                      type="email"
                      autoComplete="username"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </label>
                  <label className="admin-page__field">
                    <span>Password</span>
                    <input
                      type="password"
                      autoComplete="current-password"
                      value={supabasePassword}
                      onChange={(e) => setSupabasePassword(e.target.value)}
                      required
                    />
                  </label>
                  {authError ? (
                    <p className="admin-page__error" role="alert">
                      {authError}
                    </p>
                  ) : null}
                  <button type="submit" className="admin-page__btn" disabled={busy}>
                    {busy ? 'Signing in…' : 'Sign in to database'}
                  </button>
                </form>
              </section>
            </>
          ) : !supabaseSession.user ? (
            <section className="admin-page__panel admin-page__panel--note" role="alert">
              <h2>Session incomplete</h2>
              <p className="admin-page__muted">
                You are signed in to the database but the user profile is missing. Try signing out and signing in again,
                or check your Supabase Auth configuration.
              </p>
              <button type="button" className="admin-page__btn admin-page__btn--ghost" onClick={handleGateSignOut}>
                Sign out
              </button>
            </section>
          ) : (
            <>
              <section className="admin-page__panel admin-page__panel--toolbar">
                <p className="admin-page__signed">
                  <strong>{supabaseSession.user.email ?? 'Editor'}</strong>
                </p>
                <div className="admin-page__toolbar-actions">
                  <button type="button" className="admin-page__btn admin-page__btn--ghost" onClick={handleSupabaseSignOut}>
                    Database sign out
                  </button>
                  <button type="button" className="admin-page__btn admin-page__btn--ghost" onClick={handleGateSignOut}>
                    Sign out completely
                  </button>
                </div>
              </section>

              <section className="admin-page__panel" aria-labelledby="admin-add-h">
                <h2 id="admin-add-h">Add entry</h2>
                <form className="admin-page__form admin-page__form--grid" onSubmit={handleAdd}>
                  <label className="admin-page__field">
                    <span>Section</span>
                    <select
                      value={form.category}
                      onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
                    >
                      {MANUAL_CATEGORIES.map((c) => (
                        <option key={c} value={c}>
                          {c}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="admin-page__field">
                    <span>University</span>
                    <input
                      value={form.university}
                      onChange={(e) => setForm((f) => ({ ...f, university: e.target.value }))}
                      placeholder="e.g. RGPV"
                      required
                    />
                  </label>
                  <label className="admin-page__field admin-page__field--wide">
                    <span>Title</span>
                    <input
                      value={form.title}
                      onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
                      placeholder="Notice headline"
                      required
                    />
                  </label>
                  <label className="admin-page__field admin-page__field--wide">
                    <span>Link URL</span>
                    <input
                      type="url"
                      value={form.link_url}
                      onChange={(e) => setForm((f) => ({ ...f, link_url: e.target.value }))}
                      placeholder="https://…"
                      required
                    />
                  </label>
                  <label className="admin-page__field">
                    <span>Date</span>
                    <input
                      type="date"
                      value={form.date}
                      onChange={(e) => setForm((f) => ({ ...f, date: e.target.value }))}
                    />
                  </label>
                  <div className="admin-page__field admin-page__field--actions">
                    <button type="submit" className="admin-page__btn" disabled={busy}>
                      {busy ? 'Saving…' : 'Publish entry'}
                    </button>
                  </div>
                </form>
                {formMessage ? (
                  <p className="admin-page__ok" role="status">
                    {formMessage}
                  </p>
                ) : null}
              </section>

              <section className="admin-page__panel" aria-labelledby="admin-list-h">
                <h2 id="admin-list-h">Manual rows (database)</h2>
                <p className="admin-page__muted">
                  Rows from <code>manual_additions.json</code> are merged on the site but not listed here.
                </p>
                {listError ? (
                  <p className="admin-page__error" role="alert">
                    {listError}
                  </p>
                ) : null}
                {rows.length === 0 ? (
                  <p className="admin-page__muted">No database entries yet.</p>
                ) : (
                  <ul className="admin-page__list">
                    {rows.map((row, idx) => {
                      const item = supabaseRowToItem(row)
                      const link = item.result_url || item.url
                      return (
                        <li key={row.id != null ? String(row.id) : `row-${idx}`} className="admin-page__list-item">
                          <div className="admin-page__list-meta">
                            <span className="admin-page__badge">{row.category}</span>
                            <span className="admin-page__list-title">{item.title}</span>
                            <span className="admin-page__list-uni">{item.university}</span>
                            <a className="admin-page__list-link" href={link} target="_blank" rel="noreferrer">
                              {link}
                            </a>
                          </div>
                          <button
                            type="button"
                            className="admin-page__btn admin-page__btn--danger"
                            onClick={() => handleDelete(row.id)}
                            disabled={busy}
                          >
                            Remove
                          </button>
                        </li>
                      )
                    })}
                  </ul>
                )}
              </section>
            </>
          )}
        </div>
      </main>
      <Footer />
    </div>
  )
}
