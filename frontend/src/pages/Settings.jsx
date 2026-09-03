const CONFIG_ITEMS = [
  { label: 'LLM Provider', value: 'Anthropic (Claude)' },
  { label: 'Embedding Model', value: 'all-MiniLM-L6-v2 (local, no API key required)' },
  { label: 'Top-K Retrieval', value: '5 chunks per question' },
  { label: 'Similarity Threshold', value: '0.35' },
  { label: 'Max Context Length', value: '12,000 characters' },
  { label: 'Max Question Length', value: '2,000 characters' },
]

export function Settings() {
  return (
    <div className="mx-auto max-w-2xl px-8 py-8">
      <h1 className="text-2xl font-semibold text-ink">Settings</h1>
      <p className="mt-1 text-sm text-ink-soft">
        RAG pipeline configuration. These values are set via the backend environment and are not
        editable from this interface - there is no settings API to change them at runtime.
      </p>

      <div className="mt-6 divide-y divide-border rounded-xl border border-border bg-surface">
        {CONFIG_ITEMS.map((item) => (
          <div key={item.label} className="flex items-center justify-between px-5 py-3.5">
            <span className="text-sm text-ink-soft">{item.label}</span>
            <span className="text-sm font-medium text-ink">{item.value}</span>
          </div>
        ))}
      </div>

      <p className="mt-4 text-xs text-ink-soft">
        To change these, update <code className="rounded bg-app-bg px-1 py-0.5">backend/.env</code> and
        restart the backend. API keys are never exposed to the frontend.
      </p>
    </div>
  )
}
