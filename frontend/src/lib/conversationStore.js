// The backend persists conversations/messages internally but exposes no
// list/read endpoint for them (POST /api/chat is the only conversation API).
// To power the Conversations/History screen without inventing a backend
// endpoint, every real /api/chat exchange is also mirrored into
// localStorage here. This is real data - the exact question/answer/sources
// the backend returned - just kept client-side because there's nowhere
// else to read it back from.

const STORAGE_KEY = 'evidencerag:conversations'

function readAll() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function writeAll(conversations) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations))
  } catch {
    // Storage unavailable (private browsing, quota) - history just won't persist.
  }
}

export function listConversations() {
  return readAll().sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
}

export function getConversation(conversationId) {
  return readAll().find((c) => c.id === conversationId) || null
}

export function recordExchange({ conversationId, question, documentIds, response }) {
  const conversations = readAll()
  const now = new Date().toISOString()
  const existing = conversations.find((c) => c.id === conversationId)

  const userMessage = { role: 'user', content: question, createdAt: now }
  const assistantMessage = {
    role: 'assistant',
    content: response.answer,
    grounded: response.grounded,
    sources: response.sources,
    createdAt: now,
  }

  if (existing) {
    existing.messages.push(userMessage, assistantMessage)
    existing.updatedAt = now
    existing.documentIds = documentIds
  } else {
    conversations.push({
      id: conversationId,
      title: question,
      documentIds,
      createdAt: now,
      updatedAt: now,
      messages: [userMessage, assistantMessage],
    })
  }

  writeAll(conversations)
}

export function deleteConversation(conversationId) {
  writeAll(readAll().filter((c) => c.id !== conversationId))
}
