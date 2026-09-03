import { useEffect, useState } from 'react'
import { api } from '../api/client'

const POLL_INTERVAL_MS = 15_000

export function useHealth() {
  const [online, setOnline] = useState(null) // null = not checked yet

  useEffect(() => {
    let cancelled = false

    async function check() {
      try {
        const data = await api.getHealth()
        if (!cancelled) setOnline(data.status === 'ok')
      } catch {
        if (!cancelled) setOnline(false)
      }
    }

    check()
    const interval = setInterval(check, POLL_INTERVAL_MS)
    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [])

  return { online }
}
