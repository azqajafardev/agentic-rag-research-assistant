import { MessagesSquare, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { EmptyState } from '../components/EmptyState'
import { deleteConversation, listConversations } from '../lib/conversationStore'

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })
  } catch {
    return iso
  }
}

export function Conversations() {
  const [conversations, setConversations] = useState(() => listConversations())
  const [pendingDelete, setPendingDelete] = useState(null)

  function handleDelete(conversation) {
    deleteConversation(conversation.id)
    setConversations(listConversations())
    setPendingDelete(null)
  }

  return (
    <div className="mx-auto max-w-4xl px-8 py-8">
      <h1 className="text-2xl font-semibold text-ink">Conversations</h1>
      <p className="mt-1 text-sm text-ink-soft">
        Review and reopen your previous research conversations.
      </p>

      <div className="mt-6">
        {conversations.length === 0 ? (
          <EmptyState
            icon={MessagesSquare}
            title="No conversations yet."
            description="Start a new chat to ask questions about your documents."
          />
        ) : (
          <ul className="space-y-2">
            {conversations.map((c) => {
              const lastUserMessage = [...c.messages].reverse().find((m) => m.role === 'user')
              return (
                <li
                  key={c.id}
                  className="flex items-center justify-between gap-3 rounded-lg border border-border bg-surface px-4 py-3"
                >
                  <Link to={`/chat/${c.id}`} className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-ink">{c.title}</p>
                    <p className="mt-0.5 truncate text-xs text-ink-soft">
                      {lastUserMessage?.content}
                    </p>
                    <p className="mt-1 text-[11px] text-ink-soft">
                      {formatDate(c.updatedAt)} · {c.messages.length} messages ·{' '}
                      {c.documentIds?.length ? `${c.documentIds.length} document(s)` : 'All documents'}
                    </p>
                  </Link>
                  <button
                    type="button"
                    onClick={() => setPendingDelete(c)}
                    aria-label={`Delete conversation ${c.title}`}
                    className="shrink-0 rounded-lg p-1.5 text-ink-soft hover:bg-danger-soft hover:text-danger"
                  >
                    <Trash2 size={16} />
                  </button>
                </li>
              )
            })}
          </ul>
        )}
      </div>

      {pendingDelete && (
        <ConfirmDialog
          title="Delete this conversation?"
          description="This removes it from your local history. The backend conversation record is unaffected."
          confirmLabel="Delete"
          onCancel={() => setPendingDelete(null)}
          onConfirm={() => handleDelete(pendingDelete)}
        />
      )}
    </div>
  )
}
