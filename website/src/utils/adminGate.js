/**
 * Demo gate for /admin (client-only; credentials are visible in the built bundle).
 * Replace with a real backend or Supabase-only auth before production.
 */
const STORAGE_KEY = 'mp_admin_gate_v1'

const GATE_USERNAME = 'admin'
const GATE_PASSWORD = 'admin'

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
  if (username === GATE_USERNAME && password === GATE_PASSWORD) {
    openAdminGate()
    return true
  }
  return false
}
