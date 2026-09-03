import { AlertTriangle } from 'lucide-react'

export function ErrorBanner({ message }) {
  if (!message) return null
  return (
    <div className="flex items-start gap-2 rounded-lg border border-danger/20 bg-danger-soft px-3 py-2.5 text-sm text-danger">
      <AlertTriangle size={16} className="mt-0.5 shrink-0" />
      <span>{message}</span>
    </div>
  )
}
