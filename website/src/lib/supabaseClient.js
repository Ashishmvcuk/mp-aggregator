import { createClient } from '@supabase/supabase-js'

const url = import.meta.env.VITE_SUPABASE_URL
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

let client = null
let createFailed = false

export function isSupabaseConfigured() {
  if (createFailed) return false
  return Boolean(
    typeof url === 'string' &&
      url.startsWith('http') &&
      typeof anonKey === 'string' &&
      anonKey.length > 0
  )
}

/** @returns {import('@supabase/supabase-js').SupabaseClient | null} */
export function getSupabase() {
  if (!isSupabaseConfigured()) return null
  if (!client) {
    try {
      client = createClient(url.trim(), anonKey.trim())
    } catch (e) {
      console.error('[supabase] createClient failed:', e)
      createFailed = true
      client = null
      return null
    }
  }
  return client
}
