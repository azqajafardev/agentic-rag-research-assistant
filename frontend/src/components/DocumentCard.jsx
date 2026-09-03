import { FileText, Trash2 } from 'lucide-react'
import { StatusBadge } from './StatusBadge'

export function DocumentCard({ document, selected, onOpen, onDelete }) {
  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => onOpen(document)}
      onKeyDown={(e) => e.key === 'Enter' && onOpen(document)}
      className={`group flex cursor-pointer items-start gap-3 rounded-xl border p-3 text-left transition-colors ${
        selected
          ? 'border-accent bg-accent-soft'
          : 'border-border bg-surface hover:border-accent/40'
      }`}
    >
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-app-bg text-ink-soft">
        <FileText size={18} />
      </div>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-ink">{document.filename}</p>
        <p className="mt-0.5 text-xs text-ink-soft">
          {document.status === 'indexed'
            ? `${document.page_count} pages · ${document.chunk_count} chunks`
            : 'Processing document...'}
        </p>
        <div className="mt-2">
          <StatusBadge status={document.status} />
        </div>
      </div>
      <button
        type="button"
        aria-label={`Delete ${document.filename}`}
        onClick={(e) => {
          e.stopPropagation()
          onDelete(document)
        }}
        className="shrink-0 rounded-lg p-1.5 text-ink-soft opacity-0 transition-opacity hover:bg-danger-soft hover:text-danger group-hover:opacity-100"
      >
        <Trash2 size={16} />
      </button>
    </div>
  )
}
