import './SocialChannels.css'

export const WHATSAPP_CHANNEL_URL =
  'https://whatsapp.com/channel/0029VbCraGP84OmG2NVJJl3M'
export const TELEGRAM_CHANNEL_URL = 'https://t.me/ALLMPUNIVERSITY'

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

/**
 * @param {{ size?: 'sm' | 'md' | 'lg', showLabels?: boolean, orientation?: 'row' | 'col' }} props
 */
export function SocialChannels({ size = 'md', showLabels = false, orientation = 'row' }) {
  return (
    <div
      className={`sr-social sr-social--${size} sr-social--${orientation}`}
      role="group"
      aria-label="Join us on WhatsApp and Telegram"
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
    </div>
  )
}
