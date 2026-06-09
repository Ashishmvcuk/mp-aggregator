import { useCallback } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

/**
 * In HashRouter, `#` is used for routes; use click + scroll for same-page sections on `/`.
 */
export function SectionNavLink({ hashId, className, children }) {
  const navigate = useNavigate()
  const location = useLocation()

  const findTarget = () => {
      const candidates = Array.from(document.querySelectorAll(`[id="${hashId}"]`))
      if (candidates.length === 0) return null
      return (
        candidates.find((el) => el.offsetParent !== null || el.getClientRects().length > 0) || candidates[0]
      )
    }

    const scrollToTarget = () => {
      const target = findTarget()
      if (!target) return false
      const details = target.querySelector('details')
      if (details && !details.open) {
        details.open = true
      }
      target.scrollIntoView({ behavior: 'smooth', block: 'start' })
      return true
    }

    const attemptScroll = () => {
      if (!scrollToTarget()) {
        setTimeout(attemptScroll, 100)
      }
    }

    const onClick = useCallback(
      (e) => {
        e.preventDefault()
        if (location.pathname !== '/') {
          navigate('/')
          setTimeout(attemptScroll, 100)
        } else {
          attemptScroll()
        }
      },
      [hashId, location.pathname, navigate]
    )

  return (
    <a href={`#${hashId}`} className={className} onClick={onClick}>
      {children}
    </a>
  )
}
