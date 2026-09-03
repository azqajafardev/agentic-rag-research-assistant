import { MessagesSquare, Send, SlidersHorizontal } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ChatMessage } from '../components/ChatMessage'
import { EmptyState } from '../components/EmptyState'
import { ErrorBanner } from '../components/ErrorBanner'
import { EvidencePanel } from '../components/EvidencePanel'
import { useChat } from '../hooks/useChat'
import { useDocuments } from '../hooks/useDocuments'

export function Chat() {
  const { conversationId: routeConversationId } = useParams()
  const navigate = useNavigate()
  const { documents } = useDocuments()
  const { conversationId, messages, sending, error, send, reset } = useChat(routeConversationId)
  const [question, setQuestion] = useState('')
  const [selectedDocIds, setSelectedDocIds] = useState([])
  const [showDocPicker, setShowDocPicker] = useState(false)
  const [activeSource, setActiveSource] = useState(null)
  const bottomRef = useRef(null)

  const indexedDocuments = documents.filter((doc) => doc.status === 'indexed')

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  useEffect(() => {
    if (conversationId && conversationId !== routeConversationId) {
      navigate(`/chat/${conversationId}`, { replace: true })
    }
  }, [conversationId, routeConversationId, navigate])

  function toggleDoc(id) {
    setSelectedDocIds((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id]
    )
  }

  function handleSubmit(e) {
    e.preventDefault()
    const trimmed = question.trim()
    if (!trimmed || sending) return
    send(trimmed, selectedDocIds)
    setQuestion('')
  }

  function handleNewChat() {
    reset()
    setSelectedDocIds([])
    navigate('/chat')
  }

  const scopeLabel =
    selectedDocIds.length === 0
      ? 'All Documents'
      : `${selectedDocIds.length} document${selectedDocIds.length > 1 ? 's' : ''} selected`

  return (
    <div className="mx-auto flex h-full max-w-4xl flex-col px-8 py-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-ink">
            {messages.length === 0 ? 'New Conversation' : 'Research Assistant'}
          </h1>
          <p className="text-xs text-ink-soft">Ask questions about your uploaded papers.</p>
        </div>
        <button
          type="button"
          onClick={handleNewChat}
          className="rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-ink hover:bg-surface"
        >
          New Chat
        </button>
      </div>

      <div className="mb-4 flex flex-wrap items-center gap-2">
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowDocPicker((v) => !v)}
            className="flex items-center gap-2 rounded-lg border border-border bg-surface px-3 py-1.5 text-xs font-medium text-ink hover:border-accent/40"
          >
            <SlidersHorizontal size={14} />
            {scopeLabel}
          </button>
          {showDocPicker && (
            <div className="absolute left-0 top-full z-20 mt-2 w-64 rounded-lg border border-border bg-surface p-2 shadow-lg">
              {indexedDocuments.length === 0 ? (
                <p className="px-2 py-1.5 text-xs text-ink-soft">No indexed documents yet.</p>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={() => setSelectedDocIds([])}
                    className={`mb-1 w-full rounded-md px-2 py-1.5 text-left text-xs font-medium ${
                      selectedDocIds.length === 0 ? 'bg-accent-soft text-accent' : 'text-ink hover:bg-app-bg'
                    }`}
                  >
                    All Documents
                  </button>
                  {indexedDocuments.map((doc) => (
                    <label
                      key={doc.id}
                      className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-1.5 text-xs text-ink hover:bg-app-bg"
                    >
                      <input
                        type="checkbox"
                        checked={selectedDocIds.includes(doc.id)}
                        onChange={() => toggleDoc(doc.id)}
                      />
                      <span className="truncate">{doc.filename}</span>
                    </label>
                  ))}
                </>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto pb-4">
        {messages.length === 0 ? (
          <EmptyState
            icon={MessagesSquare}
            title="Start your research"
            description="Ask a question about your uploaded documents."
          />
        ) : (
          <div className="space-y-5">
            {messages.map((message, index) => (
              <ChatMessage
                key={index}
                message={message}
                onOpenSource={setActiveSource}
              />
            ))}
            {sending && (
              <div className="flex items-center gap-2 pl-11 text-sm text-ink-soft">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent" />
                Searching evidence and generating a grounded answer...
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {error && (
        <div className="mb-3">
          <ErrorBanner
            message={
              error.code === 'BACKEND_UNAVAILABLE'
                ? 'Backend unavailable. Please check the server.'
                : error.code === 'LLM_ERROR'
                  ? 'The AI service is currently unavailable.'
                  : error.message
            }
          />
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex items-end gap-2">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleSubmit(e)
            }
          }}
          placeholder="Ask a research question..."
          rows={1}
          className="max-h-32 flex-1 resize-none rounded-xl border border-border bg-surface px-4 py-3 text-sm text-ink placeholder:text-ink-soft focus:border-accent focus:outline-none"
        />
        <button
          type="submit"
          disabled={!question.trim() || sending}
          aria-label="Send question"
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-accent text-white hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Send size={17} />
        </button>
      </form>
      <p className="mt-2 text-center text-[11px] text-ink-soft">
        EvidenceRAG uses your documents to provide accurate, cited answers.
      </p>

      {activeSource && (
        <EvidencePanel source={activeSource} onClose={() => setActiveSource(null)} />
      )}
    </div>
  )
}
