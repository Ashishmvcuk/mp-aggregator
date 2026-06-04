/**
 * Static JSON under `public/data/` (synced by scraper), merged with manual entries.
 * Category feeds load from `public/data/*.json` (scrapper_new sync copies bucket files here).
 */

import { loadAllManualGroupedCached } from './manualEntriesService'
import { mergeWithManual } from '../utils/mergeFeedData'
import syllabusInputBundled from '../../public/data/syllabus_input.json'

const FEED_PREFIX = 'data'
/** Manually curated syllabus (`website/public/data/syllabus_input.json` — not updated by scrapers). */
const INPUT_SYLLABUS_PATH = `${FEED_PREFIX}/syllabus_input.json`

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
    const res = await fetch(dataUrl(path), { cache: 'no-store' })
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
    const base = dataUrl('data/scrape_meta.json')
    const sep = base.includes('?') ? '&' : '?'
    const url = `${base}${sep}_=${Date.now()}`
    const res = await fetch(url, { cache: 'no-store' })
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
    fetchJsonArray(`${FEED_PREFIX}/news.json`),
    fetchJsonArray(`${FEED_PREFIX}/blogs.json`),
    fetchJsonArray(`${FEED_PREFIX}/jobs.json`),
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
    fetchJsonArray(`${FEED_PREFIX}/news.json`),
    fetchJsonArray(`${FEED_PREFIX}/jobs.json`),
    loadInputSyllabus(),
    fetchJsonArray(`${FEED_PREFIX}/admit_cards.json`),
    fetchJsonArray(`${FEED_PREFIX}/enrollments.json`),
    fetchJsonArray(`${FEED_PREFIX}/blogs.json`),
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
    fetchJsonArray(`${FEED_PREFIX}/admit_cards.json`),
    loadAllManualGroupedCached().then((m) => m.admit_cards || []),
  ])
  return mergeWithManual(manual, staticItems, 'url')
}

export async function loadNews() {
  const [staticItems, manual] = await Promise.all([
    fetchJsonArray(`${FEED_PREFIX}/news.json`),
    loadAllManualGroupedCached().then((m) => m.news || []),
  ])
  return mergeWithManual(manual, staticItems, 'url')
}

/**
 * @param {unknown[]} rows
 */
function normalizeInputSyllabusRows(rows) {
  return rows
    .filter((r) => r && typeof r === 'object')
    .map((r) => ({
      university: String(r.university || '').trim(),
      title: String(r.title || '').trim(),
      url: String(r.url || '').trim(),
      date: typeof r.date === 'string' ? r.date.trim() : '',
      category: 'syllabus',
    }))
    .filter((r) => r.university && r.title && r.url)
}

/** Curated scheme/syllabus links from ``syllabus_input.json`` (bundled at build/dev compile time). */
export async function loadInputSyllabus() {
  const bundled = Array.isArray(syllabusInputBundled) ? syllabusInputBundled : []
  const fromBundle = normalizeInputSyllabusRows(bundled)
  if (fromBundle.length > 0) return fromBundle
  const fetched = await fetchJsonArray(INPUT_SYLLABUS_PATH)
  return normalizeInputSyllabusRows(fetched)
}

export async function loadSyllabus() {
  const [inputItems, manual] = await Promise.all([
    loadInputSyllabus(),
    loadAllManualGroupedCached().then((m) => m.syllabus || []),
  ])
  return mergeWithManual(manual, inputItems, 'url')
}

export async function loadEnrollments() {
  const [staticItems, manual] = await Promise.all([
    fetchJsonArray(`${FEED_PREFIX}/enrollments.json`),
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
      university: String(r.university || r.name || '').trim(),
      name: String(r.name || r.university || '').trim(),
      url: String(r.url || '').trim(),
      type: String(r.type || '').trim(),
    }))
    .filter((r) => r.university && r.url)
}

/** Per-university portal section links (Time Table, Results, etc.). */
export async function loadUniversitySections() {
  const rows = await fetchJsonArray('data/university_sections.json')
  return rows
    .filter((r) => r && typeof r === 'object')
    .map((r) => ({
      university: String(r.university || r.name || '').trim(),
      type: String(r.type || '').trim(),
      sections: Array.isArray(r.sections)
        ? r.sections
            .filter((s) => s && typeof s === 'object')
            .map((s) => ({
              label: String(s.label || '').trim(),
              url: String(s.url || '').trim(),
            }))
            .filter((s) => s.label && s.url)
        : [],
    }))
    .filter((r) => r.university && r.sections.length > 0)
}

/** National important links (`public/data/important_links.json`). */
export async function loadImportantLinks() {
  const rows = await fetchJsonArray('data/important_links.json')
  return rows
    .filter((r) => r && typeof r === 'object')
    .map((r) => ({
      category: String(r.category || '').trim(),
      organization: String(r.organization || '').trim(),
      websitelink: String(r.websitelink || r.url || '').trim(),
      logo: String(r.logo || '').trim(),
    }))
    .filter((r) => r.organization && r.websitelink)
}
