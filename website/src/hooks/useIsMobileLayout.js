import { useEffect, useState } from 'react'

/** Matches home sidebar breakpoint: collapsible tables on narrow viewports. */
const QUERY = '(max-width: 899px)'

function getInitial() {
  if (typeof window === 'undefined') return false
  return window.matchMedia(QUERY).matches
}

export function useIsMobileLayout() {
  const [isMobile, setIsMobile] = useState(getInitial)

  useEffect(() => {
    const mq = window.matchMedia(QUERY)
    const onChange = () => setIsMobile(mq.matches)
    onChange()
    mq.addEventListener('change', onChange)
    return () => mq.removeEventListener('change', onChange)
  }, [])

  return isMobile
}
