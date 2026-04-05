/** @param {string | null | undefined} iso */
export function formatDateMedium(iso) {
  if (!iso) return '—'
  try {
    return new Intl.DateTimeFormat('en-IN', {
      dateStyle: 'medium',
    }).format(new Date(iso + 'T12:00:00'))
  } catch {
    return iso
  }
}

/** Sarkari-style short date for tables (dd/MM/yyyy). */
export function formatDateShort(iso) {
  if (!iso) return '—'
  try {
    return new Intl.DateTimeFormat('en-IN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    }).format(new Date(iso + 'T12:00:00'))
  } catch {
    return iso
  }
}
