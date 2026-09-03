import { FileText, MessageSquarePlus, MessagesSquare, Upload as UploadIcon } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { EmptyState } from '../components/EmptyState'
import { LoadingState } from '../components/LoadingState'
import { StatCard } from '../components/StatCard'
import { StatusBadge } from '../components/StatusBadge'
import { UploadModal } from '../components/UploadModal'
import { useDocuments } from '../hooks/useDocuments'
import { listConversations } from '../lib/conversationStore'

export function Dashboard() {
  const { documents, loading, upload } = useDocuments()
  const [conversations, setConversations] = useState(() => listConversations())
  const [showUpload, setShowUpload] = useState(false)
  const navigate = useNavigate()

  // Re-read local conversation history when the upload modal closes, since a
  // new upload can indirectly follow with new chat activity on this page.
  useEffect(() => {
    if (!showUpload) setConversations(listConversations())
  }, [showUpload])

  const stats = useMemo(() => {
    const totalPages = documents.reduce((sum, doc) => sum + doc.page_count, 0)
    const questionsAsked = conversations.reduce((sum, c) => sum + c.messages.length / 2, 0)
    return {
      documents: documents.length,
      pages: totalPages,
      conversations: conversations.length,
      questions: Math.round(questionsAsked),
    }
  }, [documents, conversations])

  const recentDocuments = documents.slice(0, 5)
  const recentConversations = conversations.slice(0, 5)

  return (
    <div className="mx-auto max-w-6xl px-8 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Welcome back</h1>
          <p className="mt-1 text-sm text-ink-soft">
            Ask questions. Get answers grounded in your documents.
          </p>
        </div>
        <button
          type="button"
          onClick={() => navigate('/chat')}
          className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover"
        >
          <MessageSquarePlus size={16} />
          New Chat
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard icon={FileText} label="Documents" value={stats.documents} />
        <StatCard icon={FileText} label="Total Pages" value={stats.pages} />
        <StatCard icon={MessagesSquare} label="Conversations" value={stats.conversations} />
        <StatCard icon={MessagesSquare} label="Questions Asked" value={stats.questions} />
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-ink">Recent Documents</h2>
            <Link to="/documents" className="text-xs font-medium text-accent hover:underline">
              View all
            </Link>
          </div>

          {loading ? (
            <LoadingState />
          ) : recentDocuments.length === 0 ? (
            <EmptyState
              icon={UploadIcon}
              title="No research papers yet."
              description="Upload a PDF to start asking questions."
              action={
                <button
                  type="button"
                  onClick={() => setShowUpload(true)}
                  className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover"
                >
                  Upload PDFs
                </button>
              }
            />
          ) : (
            <ul className="space-y-2">
              {recentDocuments.map((doc) => (
                <li
                  key={doc.id}
                  className="flex items-center justify-between rounded-lg border border-border bg-surface px-4 py-3"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-ink">{doc.filename}</p>
                    <p className="text-xs text-ink-soft">
                      {doc.page_count} pages · {doc.chunk_count} chunks
                    </p>
                  </div>
                  <StatusBadge status={doc.status} />
                </li>
              ))}
            </ul>
          )}
        </section>

        <section>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-ink">Recent Conversations</h2>
            <Link to="/conversations" className="text-xs font-medium text-accent hover:underline">
              View all
            </Link>
          </div>

          {recentConversations.length === 0 ? (
            <EmptyState
              icon={MessagesSquare}
              title="No conversations yet."
              description="Ask a question about your uploaded documents."
            />
          ) : (
            <ul className="space-y-2">
              {recentConversations.map((c) => (
                <li key={c.id}>
                  <Link
                    to={`/chat/${c.id}`}
                    className="block truncate rounded-lg border border-border bg-surface px-4 py-3 text-sm text-ink hover:border-accent/40"
                  >
                    {c.title}
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      {showUpload && (
        <UploadModal onClose={() => setShowUpload(false)} onUpload={(files, cb) => upload(files, cb)} />
      )}
    </div>
  )
}
