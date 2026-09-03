import { X } from 'lucide-react'

export function EvidencePanel({ source, onClose }) {
  if (!source) return null
  const relevance = Math.round(source.score * 100)

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/30" onClick={onClose}>
      <div
        className="flex h-full w-full max-w-md flex-col bg-surface shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-border px-5 py-4">
          <p className="text-sm font-semibold uppercase tracking-wide text-ink-soft">
            Source Evidence
          </p>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close evidence panel"
            className="rounded-lg p-1.5 text-ink-soft hover:bg-app-bg"
          >
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-5">
          <p className="text-lg font-medium text-ink">{source.filename}</p>
          <p className="mt-1 text-sm text-ink-soft">Page {source.page}</p>

          <div className="mt-4 flex items-center gap-2">
            <span className="text-sm text-ink-soft">Relevance</span>
            <span className="rounded-full bg-accent-soft px-2.5 py-0.5 text-sm font-semibold text-accent">
              {relevance}%
            </span>
          </div>

          <hr className="my-5 border-border" />

          <p className="whitespace-pre-wrap text-sm leading-relaxed text-ink">
            {source.evidence}
          </p>
        </div>

        <div className="border-t border-border px-5 py-4">
          <button
            type="button"
            onClick={onClose}
            className="w-full rounded-lg border border-border py-2 text-sm font-medium text-ink hover:bg-app-bg"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
