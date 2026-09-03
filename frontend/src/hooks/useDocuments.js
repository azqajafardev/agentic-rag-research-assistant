import { useCallback, useEffect, useState } from 'react'
import { api } from '../api/client'

export function useDocuments() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.listDocuments()
      setDocuments(data.documents)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const upload = useCallback(
    async (files, onUploadProgress) => {
      const data = await api.uploadDocuments(files, onUploadProgress)
      await refresh()
      return data.documents
    },
    [refresh]
  )

  const remove = useCallback(
    async (documentId) => {
      await api.deleteDocument(documentId)
      setDocuments((prev) => prev.filter((doc) => doc.id !== documentId))
    },
    []
  )

  return { documents, loading, error, refresh, upload, remove }
}
