/**
 * Demo gate for /admin (client-only; credentials are visible in the built bundle).
 * Set VITE_ADMIN_USERNAME + VITE_ADMIN_PASSWORD for production-like gate, or
 * VITE_ADMIN_ALLOW_DEMO=true for local dev (admin/admin).
 */
const STORAGE_KEY = 'mp_admin_gate_v1'

// Production: set VITE_ADMIN_USERNAME/PASSWORD via secrets, or rely on Supabase only.
// Local `npm run dev`: DEV is true so admin/admin works unless env credentials override.
const allowDemo =
  import.meta.env.VITE_ADMIN_ALLOW_DEMO === 'true' || import.meta.env.DEV
const envUser =
  typeof import.meta.env.VITE_ADMIN_USERNAME === 'string'
    ? import.meta.env.VITE_ADMIN_USERNAME.trim()
    : ''
const envPass =
  typeof import.meta.env.VITE_ADMIN_PASSWORD === 'string'
    ? import.meta.env.VITE_ADMIN_PASSWORD.trim()
    : ''

export function isAdminGateOpen() {
  try {
    return sessionStorage.getItem(STORAGE_KEY) === '1'
  } catch {
    return false
  }
}

export function openAdminGate() {
  try {
    sessionStorage.setItem(STORAGE_KEY, '1')
  } catch {
    /* ignore */
  }
}

export function closeAdminGate() {
  try {
    sessionStorage.removeItem(STORAGE_KEY)
  } catch {
    /* ignore */
  }
}

export function tryAdminGateLogin(username, password) {
  if (envUser && envPass) {
    if (username === envUser && password === envPass) {
      openAdminGate()
      return true
    }
    return false
  }
  if (allowDemo && username === 'admin' && password === 'admin') {
    openAdminGate()
    return true
  }
  return false
}
