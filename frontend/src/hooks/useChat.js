import { useCallback, useState } from 'react'
import { api } from '../api/client'
import { getConversation, recordExchange } from '../lib/conversationStore'

export function useChat(initialConversationId = null) {
  const [conversationId, setConversationId] = useState(initialConversationId)
  const [messages, setMessages] = useState(() => {
    if (!initialConversationId) return []
    return getConversation(initialConversationId)?.messages || []
  })
  const [sending, setSending] = useState(false)
  const [error, setError] = useState(null)

  const send = useCallback(
    async (question, documentIds) => {
      const userMessage = { role: 'user', content: question, createdAt: new Date().toISOString() }
      setMessages((prev) => [...prev, userMessage])
      setSending(true)
      setError(null)

      try {
        const response = await api.sendChatMessage({ question, documentIds, conversationId })
        setConversationId(response.conversation_id)
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: response.answer,
            grounded: response.grounded,
            sources: response.sources,
            createdAt: new Date().toISOString(),
          },
        ])
        recordExchange({
          conversationId: response.conversation_id,
          question,
          documentIds,
          response,
        })
      } catch (err) {
        setError(err)
      } finally {
        setSending(false)
      }
    },
    [conversationId]
  )

  const reset = useCallback(() => {
    setConversationId(null)
    setMessages([])
    setError(null)
  }, [])

  return { conversationId, messages, sending, error, send, reset }
}
