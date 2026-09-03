export function StatCard({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-border bg-surface p-4 shadow-sm">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent-soft text-accent">
        <Icon size={20} strokeWidth={2} />
      </div>
      <div className="min-w-0">
        <p className="text-xl font-semibold text-ink leading-tight">{value}</p>
        <p className="truncate text-sm text-ink-soft">{label}</p>
      </div>
    </div>
  )
}
