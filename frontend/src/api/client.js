import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'

const http = axios.create({ baseURL: BASE_URL, timeout: 120_000 })

/**
 * Normalizes every failure (backend error envelope, network failure, timeout)
 * into a single shape so components never branch on axios/error internals.
 */
function toApiError(error) {
  if (error.response) {
    const payload = error.response.data
    return {
      code: payload?.error?.code || 'UNKNOWN_ERROR',
      message: payload?.error?.message || 'An unexpected error occurred.',
      status: error.response.status,
    }
  }
  if (error.request) {
    return {
      code: 'BACKEND_UNAVAILABLE',
      message: 'Backend unavailable. Please check the server.',
      status: null,
    }
  }
  return { code: 'CLIENT_ERROR', message: error.message, status: null }
}

async function request(promise) {
  try {
    const response = await promise
    return response.data
  } catch (error) {
    throw toApiError(error)
  }
}

export const api = {
  getHealth: () => request(http.get('/health')),

  listDocuments: () => request(http.get('/documents')),

  getDocument: (documentId) => request(http.get(`/documents/${documentId}`)),

  uploadDocuments: (files, onUploadProgress) => {
    const formData = new FormData()
    for (const file of files) formData.append('files', file)
    return request(
      http.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress,
      })
    )
  },

  deleteDocument: (documentId) => request(http.delete(`/documents/${documentId}`)),

  sendChatMessage: ({ question, documentIds, conversationId }) =>
    request(
      http.post('/chat', {
        question,
        document_ids: documentIds && documentIds.length > 0 ? documentIds : null,
        conversation_id: conversationId || null,
      })
    ),
}
