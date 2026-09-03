import { FileText } from 'lucide-react'

export function SourceCard({ source, index, onOpen }) {
  const relevance = Math.round(source.score * 100)

  return (
    <button
      type="button"
      onClick={() => onOpen(source)}
      className="flex w-full items-center gap-3 rounded-lg border border-border bg-surface px-3 py-2 text-left text-sm transition-colors hover:border-accent/40 hover:bg-accent-soft"
    >
      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent-soft text-xs font-semibold text-accent">
        {index + 1}
      </span>
      <FileText size={15} className="shrink-0 text-ink-soft" />
      <span className="min-w-0 flex-1 truncate text-ink">{source.filename}</span>
      <span className="shrink-0 text-xs text-ink-soft">Page {source.page}</span>
      <span className="shrink-0 rounded-full bg-app-bg px-2 py-0.5 text-xs font-medium text-ink-soft">
        {relevance}%
      </span>
    </button>
  )
}
