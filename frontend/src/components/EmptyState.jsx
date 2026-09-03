export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-border bg-surface px-6 py-14 text-center">
      {Icon && (
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-accent-soft text-accent">
          <Icon size={22} strokeWidth={2} />
        </div>
      )}
      <div>
        <p className="font-medium text-ink">{title}</p>
        {description && <p className="mt-1 max-w-sm text-sm text-ink-soft">{description}</p>}
      </div>
      {action}
    </div>
  )
}
