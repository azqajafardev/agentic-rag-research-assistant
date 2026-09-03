import { Search, Upload as UploadIcon } from 'lucide-react'
import { useMemo, useState } from 'react'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { DocumentCard } from '../components/DocumentCard'
import { DocumentDetailsPanel } from '../components/DocumentDetailsPanel'
import { EmptyState } from '../components/EmptyState'
import { ErrorBanner } from '../components/ErrorBanner'
import { LoadingState } from '../components/LoadingState'
import { UploadModal } from '../components/UploadModal'
import { useDocuments } from '../hooks/useDocuments'

const STATUS_FILTERS = ['all', 'indexed', 'processing', 'failed']

export function Documents() {
  const { documents, loading, error, upload, remove } = useDocuments()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [showUpload, setShowUpload] = useState(false)
  const [openDocument, setOpenDocument] = useState(null)
  const [pendingDelete, setPendingDelete] = useState(null)
  const [deleteError, setDeleteError] = useState(null)

  const filtered = useMemo(() => {
    return documents.filter((doc) => {
      const matchesSearch = doc.filename.toLowerCase().includes(search.toLowerCase())
      const matchesStatus = statusFilter === 'all' || doc.status === statusFilter
      return matchesSearch && matchesStatus
    })
  }, [documents, search, statusFilter])

  async function handleDelete(doc) {
    setDeleteError(null)
    try {
      await remove(doc.id)
      setPendingDelete(null)
      setOpenDocument(null)
    } catch (err) {
      setDeleteError(err.message || 'Failed to delete document.')
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-8 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Documents</h1>
          <p className="mt-1 text-sm text-ink-soft">Manage your uploaded research papers.</p>
        </div>
        <button
          type="button"
          onClick={() => setShowUpload(true)}
          className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover"
        >
          <UploadIcon size={16} />
          Upload
        </button>
      </div>

      <div className="mb-5 flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search
            size={16}
            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-soft"
          />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search documents..."
            className="w-full rounded-lg border border-border bg-surface py-2 pl-9 pr-3 text-sm text-ink placeholder:text-ink-soft focus:border-accent focus:outline-none"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-border bg-surface px-3 py-2 text-sm text-ink focus:border-accent focus:outline-none"
        >
          {STATUS_FILTERS.map((status) => (
            <option key={status} value={status}>
              {status === 'all' ? 'All Statuses' : status[0].toUpperCase() + status.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {deleteError && (
        <div className="mb-4">
          <ErrorBanner message={deleteError} />
        </div>
      )}
      {error && (
        <div className="mb-4">
          <ErrorBanner message={error.message} />
        </div>
      )}

      {loading ? (
        <LoadingState />
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={UploadIcon}
          title={documents.length === 0 ? 'No research papers yet.' : 'No documents match your filters.'}
          description={
            documents.length === 0 ? 'Upload a PDF to start asking questions.' : undefined
          }
          action={
            documents.length === 0 && (
              <button
                type="button"
                onClick={() => setShowUpload(true)}
                className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover"
              >
                Upload PDFs
              </button>
            )
          }
        />
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {filtered.map((doc) => (
            <DocumentCard
              key={doc.id}
              document={doc}
              onOpen={setOpenDocument}
              onDelete={setPendingDelete}
            />
          ))}
        </div>
      )}

      {showUpload && (
        <UploadModal onClose={() => setShowUpload(false)} onUpload={(files, cb) => upload(files, cb)} />
      )}

      {openDocument && (
        <DocumentDetailsPanel
          document={openDocument}
          onClose={() => setOpenDocument(null)}
          onDelete={setPendingDelete}
        />
      )}

      {pendingDelete && (
        <ConfirmDialog
          title={`Delete "${pendingDelete.filename}"?`}
          description="This permanently removes the document and its indexed evidence. This cannot be undone."
          confirmLabel="Delete"
          onCancel={() => setPendingDelete(null)}
          onConfirm={() => handleDelete(pendingDelete)}
        />
      )}
    </div>
  )
}
