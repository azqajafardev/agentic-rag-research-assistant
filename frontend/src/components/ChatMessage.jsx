import { AlertCircle, Brain } from 'lucide-react'
import { SourceCard } from './SourceCard'

function formatTime(iso) {
  try {
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ''
  }
}

export function ChatMessage({ message, onOpenSource }) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-2xl rounded-2xl rounded-tr-sm bg-accent px-4 py-3 text-sm text-white shadow-sm">
          {message.content}
          <p className="mt-1 text-right text-[11px] text-white/70">
            {formatTime(message.createdAt)}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-start gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent-soft text-accent">
        <Brain size={16} />
      </div>
      <div className="max-w-2xl flex-1">
        <div className="rounded-2xl rounded-tl-sm border border-border bg-surface px-4 py-3 text-sm text-ink shadow-sm">
          {message.grounded === false && (
            <div className="mb-2 flex items-center gap-2 text-ink-soft">
              <AlertCircle size={15} />
              <span className="text-xs font-medium uppercase tracking-wide">
                No evidence found
              </span>
            </div>
          )}
          <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
          <p className="mt-1 text-[11px] text-ink-soft">{formatTime(message.createdAt)}</p>
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 space-y-2">
            <p className="text-xs font-semibold uppercase tracking-wide text-ink-soft">
              Sources
            </p>
            {message.sources.map((source, index) => (
              <SourceCard
                key={source.id}
                source={source}
                index={index}
                onOpen={onOpenSource}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
