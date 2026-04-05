import { useCallback } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

/**
 * In HashRouter, `#` is used for routes; use click + scroll for same-page sections on `/`.
 */
export function SectionNavLink({ hashId, className, children }) {
  const navigate = useNavigate()
  const location = useLocation()

  const onClick = useCallback(
    (e) => {
      e.preventDefault()
      const el = () => document.getElementById(hashId)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      if (location.pathname !== '/') {
        navigate('/')
        setTimeout(el, 80)
      } else {
        el()
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
