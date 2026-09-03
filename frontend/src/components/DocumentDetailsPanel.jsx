import { Trash2, X } from 'lucide-react'
import { StatusBadge } from './StatusBadge'

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString([], {
      dateStyle: 'medium',
      timeStyle: 'short',
    })
  } catch {
    return iso
  }
}

function Field({ label, value }) {
  return (
    <div>
      <p className="text-xs font-medium uppercase tracking-wide text-ink-soft">{label}</p>
      <p className="mt-0.5 text-sm text-ink">{value}</p>
    </div>
  )
}

export function DocumentDetailsPanel({ document, onClose, onDelete }) {
  if (!document) return null

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/30" onClick={onClose}>
      <div
        className="flex h-full w-full max-w-md flex-col bg-surface shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-border px-5 py-4">
          <p className="text-sm font-semibold uppercase tracking-wide text-ink-soft">
            Document Details
          </p>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close document details"
            className="rounded-lg p-1.5 text-ink-soft hover:bg-app-bg"
          >
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 space-y-5 overflow-y-auto px-5 py-5">
          <div>
            <p className="break-words text-lg font-medium text-ink">{document.filename}</p>
            <div className="mt-2">
              <StatusBadge status={document.status} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Field label="Pages" value={document.page_count} />
            <Field label="Chunks" value={document.chunk_count} />
          </div>

          <Field label="Document ID" value={document.id} />
          <Field label="Uploaded" value={formatDate(document.created_at)} />
          <Field label="Last Updated" value={formatDate(document.updated_at)} />
        </div>

        <div className="border-t border-border px-5 py-4">
          <button
            type="button"
            onClick={() => onDelete(document)}
            className="flex w-full items-center justify-center gap-2 rounded-lg border border-danger/30 py-2 text-sm font-medium text-danger hover:bg-danger-soft"
          >
            <Trash2 size={15} />
            Delete Document
          </button>
        </div>
      </div>
    </div>
  )
}
