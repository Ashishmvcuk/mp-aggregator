/**
 * Static JSON under `public/data/` (synced by scraper), merged with manual entries.
 */

import { loadAllManualGroupedCached } from './manualEntriesService'
import { mergeWithManual } from '../utils/mergeFeedData'

function dataUrl(path) {
  const base = import.meta.env.BASE_URL || '/'
  const p = path.replace(/^\//, '')
  return `${base}${p}`
}

/**
 * @param {string} path e.g. `data/news.json`
 * @returns {Promise<Array<Record<string, unknown>>>}
 */
export async function fetchJsonArray(path) {
  try {
    const res = await fetch(dataUrl(path))
    if (!res.ok) return []
    const data = await res.json()
    return Array.isArray(data) ? data : []
  } catch {
    return []
  }
}

/**
 * Runtime scrape metadata (`public/data/scrape_meta.json`), updated when CI/local sync runs.
 * @returns {Promise<Record<string, unknown> | null>}
 */
export async function fetchScrapeMeta() {
  try {
    const res = await fetch(dataUrl('data/scrape_meta.json'), { cache: 'no-store' })
    if (!res.ok) return null
    const data = await res.json()
    if (!data || typeof data !== 'object' || Array.isArray(data)) return null
    return data
  } catch {
    return null
  }
}

export async function loadDashboardFeeds() {
  const [news, blogs, jobs, manual] = await Promise.all([
    fetchJsonArray('data/news.json'),
    fetchJsonArray('data/blogs.json'),
    fetchJsonArray('data/jobs.json'),
    loadAllManualGroupedCached(),
  ])
  return {
    news: mergeWithManual(manual.news, news, 'url'),
    blogs: mergeWithManual(manual.blogs, blogs, 'url'),
    jobs: mergeWithManual(manual.jobs, jobs, 'url'),
  }
}

/** All category feeds used on the landing page (except results — loaded separately). */
export async function loadLandingFeeds() {
  const [news, jobs, syllabus, admit_cards, enrollments, blogs, manual] = await Promise.all([
    fetchJsonArray('data/news.json'),
    fetchJsonArray('data/jobs.json'),
    fetchJsonArray('data/syllabus.json'),
    fetchJsonArray('data/admit_cards.json'),
    fetchJsonArray('data/enrollments.json'),
    fetchJsonArray('data/blogs.json'),
    loadAllManualGroupedCached(),
  ])
  return {
    news: mergeWithManual(manual.news, news, 'url'),
    jobs: mergeWithManual(manual.jobs, jobs, 'url'),
    syllabus: mergeWithManual(manual.syllabus, syllabus, 'url'),
    admit_cards: mergeWithManual(manual.admit_cards, admit_cards, 'url'),
    enrollments: mergeWithManual(manual.enrollments, enrollments, 'url'),
    blogs: mergeWithManual(manual.blogs, blogs, 'url'),
  }
}

export async function loadAdmitCards() {
  const [staticItems, manual] = await Promise.all([
    fetchJsonArray('data/admit_cards.json'),
    loadAllManualGroupedCached().then((m) => m.admit_cards || []),
  ])
  return mergeWithManual(manual, staticItems, 'url')
}

export async function loadEnrollments() {
  const [staticItems, manual] = await Promise.all([
    fetchJsonArray('data/enrollments.json'),
    loadAllManualGroupedCached().then((m) => m.enrollments || []),
  ])
  return mergeWithManual(manual, staticItems, 'url')
}

/** Enabled universities from `public/data/universities.json` (synced from scraper config). */
export async function loadUniversityPortals() {
  const rows = await fetchJsonArray('data/universities.json')
  return rows
    .filter((r) => r && typeof r === 'object')
    .map((r) => ({
      university: String(r.university || '').trim(),
      url: String(r.url || '').trim(),
    }))
    .filter((r) => r.university && r.url)
}
