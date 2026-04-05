/**
 * Manual entries: optional `manual_additions.json` + optional Supabase `manual_entries` table.
 */

import { getSupabase, isSupabaseConfigured } from '../lib/supabaseClient'
import { mergeWithManual } from '../utils/mergeFeedData'

function dataUrl(path) {
  const base = import.meta.env.BASE_URL || '/'
  const p = path.replace(/^\//, '')
  return `${base}${p}`
}

export const MANUAL_CATEGORIES = [
  'results',
  'news',
  'jobs',
  'syllabus',
  'admit_cards',
  'blogs',
]

/** @param {string} category */
export function linkKeyForCategory(category) {
  return category === 'results' ? 'result_url' : 'url'
}

/**
 * @param {Record<string, unknown>} row
 */
export function supabaseRowToItem(row) {
  const cat = String(row.category || '')
  const base = {
    university: String(row.university || ''),
    title: String(row.title || ''),
    date: String(row.date || ''),
  }
  const link = String(row.link_url || '')
  if (cat === 'results') {
    return { ...base, result_url: link }
  }
  return { ...base, url: link }
}

const EMPTY_FILE = () =>
  Object.fromEntries(MANUAL_CATEGORIES.map((c) => [c, []]))

/** @returns {Promise<Record<string, unknown[]>>} */
export async function fetchManualAdditionsFile() {
  try {
    const res = await fetch(dataUrl('data/manual_additions.json'), { cache: 'no-store' })
    if (!res.ok) return EMPTY_FILE()
    const data = await res.json()
    if (!data || typeof data !== 'object' || Array.isArray(data)) return EMPTY_FILE()
    const out = EMPTY_FILE()
    for (const c of MANUAL_CATEGORIES) {
      const arr = data[c]
      out[c] = Array.isArray(arr) ? arr.filter((x) => x && typeof x === 'object') : []
    }
    return out
  } catch {
    return EMPTY_FILE()
  }
}

/** @returns {Promise<Record<string, unknown>[]>} */
async function fetchAllSupabaseRows() {
  const sb = getSupabase()
  if (!sb) return []
  const { data, error } = await sb.from('manual_entries').select('*').order('created_at', { ascending: false })
  if (error) {
    console.warn('[manual_entries]', error.message)
    return []
  }
  return Array.isArray(data) ? data : []
}

/** @returns {Promise<Record<string, unknown[]>>} */
async function manualFromSupabaseByCategory() {
  const rows = await fetchAllSupabaseRows()
  const grouped = EMPTY_FILE()
  for (const row of rows) {
    const cat = String(row.category || '')
    if (!MANUAL_CATEGORIES.includes(cat)) continue
    grouped[cat].push(supabaseRowToItem(row))
  }
  return grouped
}

/**
 * Merge file + DB manual lists per category (file first, then DB, deduped by link).
 * @returns {Promise<Record<string, unknown[]>>}
 */
export async function loadAllManualGrouped() {
  const [file, db] = await Promise.all([fetchManualAdditionsFile(), manualFromSupabaseByCategory()])
  const out = EMPTY_FILE()
  for (const c of MANUAL_CATEGORIES) {
    const key = linkKeyForCategory(c)
    out[c] = mergeWithManual(file[c] || [], db[c] || [], key)
  }
  return out
}

let _manualGroupedPromise = null

/** One fetch per full page load; call `resetManualEntriesCache()` after admin edits. */
export async function loadAllManualGroupedCached() {
  if (!_manualGroupedPromise) {
    _manualGroupedPromise = loadAllManualGrouped()
  }
  return _manualGroupedPromise
}

export function resetManualEntriesCache() {
  _manualGroupedPromise = null
}

/**
 * @param {string} category
 * @returns {Promise<unknown[]>}
 */
export async function getManualItemsForCategory(category) {
  if (!MANUAL_CATEGORIES.includes(category)) return []
  const all = await loadAllManualGroupedCached()
  return all[category] || []
}

export { isSupabaseConfigured }
