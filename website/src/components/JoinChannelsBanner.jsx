import { TELEGRAM_CHANNEL_URL, WHATSAPP_CHANNEL_URL } from './SocialChannels'
import './JoinChannelsBanner.css'

function WhatsAppGlyph() {
  return (
    <svg
      className="join-strip__glyph"
      viewBox="0 0 32 32"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <path
        fill="#fff"
        d="M22.27 19.33c-.3-.15-1.77-.87-2.05-.97-.27-.1-.48-.15-.68.15-.2.3-.78.97-.95 1.17-.17.2-.35.23-.65.08-.3-.15-1.26-.47-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.14-.14.3-.35.45-.53.15-.18.2-.3.3-.5.1-.2.05-.38-.03-.53-.08-.15-.68-1.64-.93-2.24-.24-.58-.49-.5-.68-.51l-.58-.01c-.2 0-.53.08-.8.38-.28.3-1.05 1.03-1.05 2.5 0 1.48 1.08 2.9 1.23 3.1.15.2 2.13 3.26 5.17 4.57.72.31 1.29.5 1.73.64.73.23 1.4.2 1.92.12.58-.09 1.77-.72 2.02-1.42.25-.7.25-1.3.18-1.42-.08-.13-.28-.2-.58-.35z"
      />
    </svg>
  )
}

function TelegramGlyph() {
  return (
    <svg
      className="join-strip__glyph"
      viewBox="0 0 32 32"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <path
        fill="#fff"
        d="M22.5 10.2 20.1 22c-.18.8-.66 1-1.33.62l-3.67-2.7-1.77 1.7c-.2.2-.37.37-.74.37l.26-3.7 6.74-6.1c.3-.26-.07-.4-.46-.15l-8.33 5.24-3.6-1.12c-.78-.24-.8-.78.16-1.15l14.08-5.44c.65-.23 1.22.15 1.07 1.13z"
      />
    </svg>
  )
}

export function JoinChannelsBanner() {
  return (
    <aside
      className="join-strip"
      role="region"
      aria-label="Join All MP University Updates channels"
    >
      <div className="join-strip__inner">
        <p className="join-strip__msg">
          <span className="join-strip__bell" aria-hidden="true">🔔</span>
          <strong>Get latest information / results / admit cards</strong>
        </p>
        <div className="join-strip__actions">
          <a
            className="join-strip__btn join-strip__btn--whatsapp"
            href={WHATSAPP_CHANNEL_URL}
            target="_blank"
            rel="noopener noreferrer"
          >
            <span className="join-strip__badge join-strip__badge--whatsapp">
              <WhatsAppGlyph />
            </span>
            <span className="join-strip__btn-name">Join WhatsApp</span>
          </a>
          <a
            className="join-strip__btn join-strip__btn--telegram"
            href={TELEGRAM_CHANNEL_URL}
            target="_blank"
            rel="noopener noreferrer"
          >
            <span className="join-strip__badge join-strip__badge--telegram">
              <TelegramGlyph />
            </span>
            <span className="join-strip__btn-name">Join Telegram</span>
          </a>
        </div>
      </div>
    </aside>
  )
}
