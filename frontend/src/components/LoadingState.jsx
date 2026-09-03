import { Loader2 } from 'lucide-react'

export function LoadingState({ label = 'Loading...' }) {
  return (
    <div className="flex items-center justify-center gap-2 py-14 text-sm text-ink-soft">
      <Loader2 size={16} className="animate-spin" />
      {label}
    </div>
  )
}
