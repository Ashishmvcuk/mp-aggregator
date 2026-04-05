/**
 * Data access for university results.
 * Swap `fetchLocalResults` for an API client when the backend/scraper is ready.
 */

const LOCAL_JSON_PATH = `${import.meta.env.BASE_URL}results.json`

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
  return fetchLocalResults()
}
