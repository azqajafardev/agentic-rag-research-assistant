const STATUS_STYLES = {
  indexed: { label: 'Indexed', dot: 'bg-success', text: 'text-success', bg: 'bg-success-soft' },
  processing: {
    label: 'Processing',
    dot: 'bg-warning',
    text: 'text-warning',
    bg: 'bg-warning-soft',
  },
  uploaded: {
    label: 'Uploaded',
    dot: 'bg-warning',
    text: 'text-warning',
    bg: 'bg-warning-soft',
  },
  failed: { label: 'Failed', dot: 'bg-danger', text: 'text-danger', bg: 'bg-danger-soft' },
}

export function StatusBadge({ status }) {
  const style = STATUS_STYLES[status] || {
    label: status,
    dot: 'bg-ink-soft',
    text: 'text-ink-soft',
    bg: 'bg-app-bg',
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${style.bg} ${style.text}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${style.dot}`} aria-hidden="true" />
      {style.label}
    </span>
  )
}
