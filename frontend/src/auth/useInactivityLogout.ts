import { useEffect, useRef } from 'react'

export function useInactivityLogout(opts: { enabled: boolean; timeoutMs: number; onTimeout: () => void }) {
  const { enabled, timeoutMs, onTimeout } = opts
  const timer = useRef<number | null>(null)

  useEffect(() => {
    if (!enabled) return

    const reset = () => {
      if (timer.current) window.clearTimeout(timer.current)
      timer.current = window.setTimeout(() => onTimeout(), timeoutMs)
    }

    const events = ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll'] as const
    events.forEach((ev) => window.addEventListener(ev, reset, { passive: true }))

    reset()

    return () => {
      if (timer.current) window.clearTimeout(timer.current)
      events.forEach((ev) => window.removeEventListener(ev, reset))
    }
  }, [enabled, timeoutMs, onTimeout])
}
