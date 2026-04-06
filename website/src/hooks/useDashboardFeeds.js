import { useEffect, useMemo, useState } from 'react'
import { loadLandingFeeds } from '../services/dashboardDataService'
import { isWithinLastDays, sortByDateDesc } from '../utils/dateRange'

const NEWS_DAYS = 30
const MAX_NEWS = 45
const MAX_ENROLLMENT_SIDEBAR = 10
const MAX_JOBS = 40
const MAX_SYLLABUS = 30
const MAX_ADMIT_HOME = 15
const MAX_BLOGS = 25

/**
 * @typedef {Object} FeedItem
 * @property {string} university
 * @property {string} title
 * @property {string} url
 * @property {string} date
 */

export function useDashboardFeeds() {
  const [news, setNews] = useState(/** @type {FeedItem[]} */ ([]))
  const [blogs, setBlogs] = useState(/** @type {FeedItem[]} */ ([]))
  const [jobs, setJobs] = useState(/** @type {FeedItem[]} */ ([]))
  const [syllabus, setSyllabus] = useState(/** @type {FeedItem[]} */ ([]))
  const [admitCards, setAdmitCards] = useState(/** @type {FeedItem[]} */ ([]))
  const [enrollments, setEnrollments] = useState(/** @type {FeedItem[]} */ ([]))
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(/** @type {string|null} */ (null))

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    loadLandingFeeds()
      .then(({ news: n, blogs: b, jobs: j, syllabus: s, admit_cards: a, enrollments: e }) => {
        if (cancelled) return
        setNews(n)
        setBlogs(b)
        setJobs(j)
        setSyllabus(s)
        setAdmitCards(a)
        setEnrollments(e)
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load feeds')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const newsLast30Days = useMemo(() => {
    const filtered = news.filter((item) => isWithinLastDays(item.date, NEWS_DAYS))
    return sortByDateDesc(filtered).slice(0, MAX_NEWS)
  }, [news])

  const jobsSorted = useMemo(() => sortByDateDesc(jobs).slice(0, MAX_JOBS), [jobs])

  const syllabusSorted = useMemo(() => sortByDateDesc(syllabus).slice(0, MAX_SYLLABUS), [syllabus])

  const admitCardsSorted = useMemo(() => sortByDateDesc(admitCards), [admitCards])

  const admitCardsHomePreview = useMemo(
    () => admitCardsSorted.slice(0, MAX_ADMIT_HOME),
    [admitCardsSorted]
  )

  const blogsSorted = useMemo(() => sortByDateDesc(blogs).slice(0, MAX_BLOGS), [blogs])

  const enrollmentsSorted = useMemo(() => sortByDateDesc(enrollments), [enrollments])

  const enrollmentsPreview = useMemo(
    () => enrollmentsSorted.slice(0, MAX_ENROLLMENT_SIDEBAR),
    [enrollmentsSorted]
  )

  const enrollmentsTotal = enrollmentsSorted.length

  return {
    enrollmentsPreview,
    enrollmentsTotal,
    newsLast30Days,
    jobsSorted,
    syllabusSorted,
    admitCardsHomePreview,
    admitCardsTotal: admitCardsSorted.length,
    blogsSorted,
    loading,
    error,
  }
}
