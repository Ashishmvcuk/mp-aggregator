import { createClient } from '@supabase/supabase-js'

const urlRaw = import.meta.env.VITE_SUPABASE_URL
const anonKeyRaw = import.meta.env.VITE_SUPABASE_ANON_KEY

const url = typeof urlRaw === 'string' ? urlRaw.trim() : ''
const anonKey = typeof anonKeyRaw === 'string' ? anonKeyRaw.trim() : ''

let client = null
let createFailed = false

export function isSupabaseConfigured() {
  if (createFailed) return false
  return Boolean(url.startsWith('http') && anonKey.length > 0)
}

/** @returns {import('@supabase/supabase-js').SupabaseClient | null} */
export function getSupabase() {
  if (!isSupabaseConfigured()) return null
  if (!client) {
    try {
      client = createClient(url, anonKey)
    } catch (e) {
      console.error('[supabase] createClient failed:', e)
      createFailed = true
      client = null
      return null
    }
  }
  return client
}
