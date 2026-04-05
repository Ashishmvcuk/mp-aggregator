import { createClient } from '@supabase/supabase-js'

const url = import.meta.env.VITE_SUPABASE_URL
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

let client = null

export function isSupabaseConfigured() {
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
    client = createClient(url, anonKey)
  }
  return client
}
