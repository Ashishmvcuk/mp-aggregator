import { InstagramIcon } from './icons/InstagramIcon'
import './SocialChannels.css'

export const WHATSAPP_CHANNEL_URL =
  'https://whatsapp.com/channel/0029VbCraGP84OmG2NVJJl3M'
export const TELEGRAM_CHANNEL_URL = 'https://t.me/ALLMPUNIVERSITY'
export const X_PROFILE_URL = 'https://x.com/AllmpUNIVERSITY'
export const INSTAGRAM_PROFILE_URL =
  'https://www.instagram.com/allmpuniversity/?hl=en'
export const LINKEDIN_PROFILE_URL = 'https://www.linkedin.com/in/allmp-university-59a473406/'

function WhatsAppIcon({ className }) {
  return (
    <svg
      className={className}
      viewBox="0 0 32 32"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <path
        fill="#25D366"
        d="M16 3C8.82 3 3 8.82 3 16c0 2.29.6 4.43 1.64 6.29L3 29l6.89-1.62A12.94 12.94 0 0 0 16 29c7.18 0 13-5.82 13-13S23.18 3 16 3z"
      />
      <path
        fill="#fff"
        d="M22.27 19.33c-.3-.15-1.77-.87-2.05-.97-.27-.1-.48-.15-.68.15-.2.3-.78.97-.95 1.17-.17.2-.35.23-.65.08-.3-.15-1.26-.47-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.14-.14.3-.35.45-.53.15-.18.2-.3.3-.5.1-.2.05-.38-.03-.53-.08-.15-.68-1.64-.93-2.24-.24-.58-.49-.5-.68-.51l-.58-.01c-.2 0-.53.08-.8.38-.28.3-1.05 1.03-1.05 2.5 0 1.48 1.08 2.9 1.23 3.1.15.2 2.13 3.26 5.17 4.57.72.31 1.29.5 1.73.64.73.23 1.4.2 1.92.12.58-.09 1.77-.72 2.02-1.42.25-.7.25-1.3.18-1.42-.08-.13-.28-.2-.58-.35z"
      />
    </svg>
  )
}

function TelegramIcon({ className }) {
  return (
    <svg
      className={className}
      viewBox="0 0 32 32"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <circle cx="16" cy="16" r="13" fill="#229ED9" />
      <path
        fill="#fff"
        d="M22.5 10.2 20.1 22c-.18.8-.66 1-1.33.62l-3.67-2.7-1.77 1.7c-.2.2-.37.37-.74.37l.26-3.7 6.74-6.1c.3-.26-.07-.4-.46-.15l-8.33 5.24-3.6-1.12c-.78-.24-.8-.78.16-1.15l14.08-5.44c.65-.23 1.22.15 1.07 1.13z"
      />
    </svg>
  )
}

function XIcon({ className }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <rect width="24" height="24" rx="5" fill="#000" />
      <path
        fill="#fff"
        d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"
      />
    </svg>
  )
}

function LinkedInIcon({ className }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <rect width="24" height="24" rx="5" fill="#0A66C2" />
      <path
        fill="#fff"
        d="M6.94 8.61H4.5v10.02h2.44V8.61zm-1.22-2.07c.79 0 1.28-.53 1.28-1.2-.01-.68-.49-1.2-1.27-1.2-.78 0-1.28.52-1.28 1.2 0 .67.49 1.2 1.27 1.2h.01zm6.95 2.07h-2.34v10.02h2.34V14.1c0-1.67.31-3.24 2.35-3.24 2.03 0 2.04 1.78 2.04 3.34v4.82h2.34v-5.18c0-2.78-.59-4.92-4.21-4.92-1.96 0-2.8 1.08-3.27 1.84h.01z"
      />
    </svg>
  )
}

/**
 * @param {{ size?: 'sm' | 'md' | 'lg', showLabels?: boolean, orientation?: 'row' | 'col' }} props
 */
export function SocialChannels({ size = 'md', showLabels = false, orientation = 'row' }) {
  return (
    <div
      className={`sr-social sr-social--${size} sr-social--${orientation}`}
      role="group"
      aria-label="Follow us on WhatsApp, Telegram, X, LinkedIn, and Instagram"
    >
      <a
        className="sr-social__link sr-social__link--whatsapp"
        href={WHATSAPP_CHANNEL_URL}
        target="_blank"
        rel="noopener noreferrer"
        aria-label="Join WhatsApp channel for updates"
      >
        <WhatsAppIcon className="sr-social__icon" />
        {showLabels && <span className="sr-social__label">WhatsApp</span>}
      </a>
      <a
        className="sr-social__link sr-social__link--telegram"
        href={TELEGRAM_CHANNEL_URL}
        target="_blank"
        rel="noopener noreferrer"
        aria-label="Join Telegram channel for updates"
      >
        <TelegramIcon className="sr-social__icon" />
        {showLabels && <span className="sr-social__label">Telegram</span>}
      </a>
      <a
        className="sr-social__link sr-social__link--x"
        href={X_PROFILE_URL}
        target="_blank"
        rel="noopener noreferrer"
        aria-label="Follow on X (Twitter)"
      >
        <XIcon className="sr-social__icon" />
        {showLabels && <span className="sr-social__label">X</span>}
      </a>
      <a
        className="sr-social__link sr-social__link--linkedin"
        href={LINKEDIN_PROFILE_URL}
        target="_blank"
        rel="noopener noreferrer"
        aria-label="Follow on LinkedIn"
      >
        <LinkedInIcon className="sr-social__icon" />
        {showLabels && <span className="sr-social__label">LinkedIn</span>}
      </a>
      <a
        className="sr-social__link sr-social__link--instagram"
        href={INSTAGRAM_PROFILE_URL}
        target="_blank"
        rel="noopener noreferrer"
        aria-label="Follow on Instagram"
      >
        <InstagramIcon className="sr-social__icon" />
        {showLabels && <span className="sr-social__label">Instagram</span>}
      </a>
    </div>
  )
}
