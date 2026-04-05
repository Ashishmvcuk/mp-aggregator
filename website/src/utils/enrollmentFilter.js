/**
 * Heuristic: news items that look like open enrollment, admissions, or related notices.
 * @param {{ title?: string; url?: string }} item
 */
export function isEnrollmentRelated(item) {
  const text = `${item.title || ''} ${item.url || ''}`.toLowerCase()
  if (
    /\b(admit\s*card|hall\s*ticket|answer\s*key|time\s*table|timetable|revaluation|rechecking)\b/i.test(
      text
    )
  ) {
    return false
  }
  return (
    /\b(enroll|enrol)\w*\b/i.test(text) ||
    /\badmission\b/i.test(text) ||
    /\b(counselling|counseling)\b/i.test(text) ||
    /\bprospectus\b/i.test(text) ||
    /\bspot\s+(counselling|counseling|admission)\b/i.test(text) ||
    /\bapplication\s+form\b/i.test(text)
  )
}
