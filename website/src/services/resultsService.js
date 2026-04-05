/**
 * Data access for university results.
 * Static file path matches scraper output: `website/public/data/results.json`.
 * Merges `manual_additions.json` + optional Supabase `manual_entries` (see manualEntriesService).
 */

import { getManualItemsForCategory } from './manualEntriesService'
import { mergeWithManual } from '../utils/mergeFeedData'

const LOCAL_JSON_PATH = `${import.meta.env.BASE_URL}data/results.json`

/**
 * @typedef {Object} UniversityResult
 * @property {string} university
 * @property {string} title
 * @property {string} result_url
 * @property {string} date  ISO date string (YYYY-MM-DD)
 */

/**
 * Load results from the static JSON shipped with the app (mock / scraper output).
 * @returns {Promise<UniversityResult[]>}
 */
export async function fetchLocalResults() {
  const res = await fetch(LOCAL_JSON_PATH)
  if (!res.ok) {
    throw new Error(`Failed to load results: ${res.status}`)
  }
  const data = await res.json()
  if (!Array.isArray(data)) {
    throw new Error('Invalid results payload: expected an array')
  }
  return data
}

/**
 * Future: replace with `fetch('/api/results')` or similar.
 * @returns {Promise<UniversityResult[]>}
 */
export async function fetchResults() {
  const [staticList, manual] = await Promise.all([
    fetchLocalResults(),
    getManualItemsForCategory('results'),
  ])
  return mergeWithManual(manual, staticList, 'result_url')
}
