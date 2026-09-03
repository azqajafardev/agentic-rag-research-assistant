import { CheckCircle2, File as FileIcon, Upload, X, XCircle } from 'lucide-react'
import { useRef, useState } from 'react'

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export function UploadModal({ onClose, onUpload }) {
  const [files, setFiles] = useState([])
  const [dragging, setDragging] = useState(false)
  const [phase, setPhase] = useState('idle') // idle | uploading | done
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)

  function addFiles(fileList) {
    const pdfFiles = Array.from(fileList).filter((f) => f.name.toLowerCase().endsWith('.pdf'))
    setFiles((prev) => [...prev, ...pdfFiles])
  }

  function removeFile(index) {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  async function handleUpload() {
    if (files.length === 0) return
    setPhase('uploading')
    setError(null)
    try {
      const uploaded = await onUpload(files, (evt) => {
        if (evt.total) setProgress(Math.round((evt.loaded / evt.total) * 100))
      })
      setResults(uploaded)
      setPhase('done')
    } catch (err) {
      setError(err.message || 'Upload failed.')
      setPhase('idle')
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4">
      <div className="w-full max-w-md rounded-2xl bg-surface p-6 shadow-xl">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-ink">Upload Documents</h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close upload dialog"
            className="rounded-lg p-1.5 text-ink-soft hover:bg-app-bg"
          >
            <X size={18} />
          </button>
        </div>

        {phase !== 'done' && (
          <>
            <div
              onDragOver={(e) => {
                e.preventDefault()
                setDragging(true)
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={(e) => {
                e.preventDefault()
                setDragging(false)
                addFiles(e.dataTransfer.files)
              }}
              className={`flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed px-6 py-10 text-center transition-colors ${
                dragging ? 'border-accent bg-accent-soft' : 'border-border bg-app-bg'
              }`}
            >
              <Upload size={24} className="text-accent" />
              <p className="text-sm text-ink">
                Drag and drop PDF files here or{' '}
                <button
                  type="button"
                  onClick={() => inputRef.current?.click()}
                  className="font-medium text-accent underline-offset-2 hover:underline"
                >
                  click to browse
                </button>
              </p>
              <p className="text-xs text-ink-soft">Supports PDF files</p>
              <input
                ref={inputRef}
                type="file"
                accept="application/pdf"
                multiple
                hidden
                onChange={(e) => addFiles(e.target.files)}
              />
            </div>

            {files.length > 0 && (
              <ul className="mt-4 max-h-40 space-y-2 overflow-y-auto">
                {files.map((file, index) => (
                  <li
                    key={`${file.name}-${index}`}
                    className="flex items-center gap-2 rounded-lg border border-border px-3 py-2 text-sm"
                  >
                    <FileIcon size={15} className="shrink-0 text-ink-soft" />
                    <span className="min-w-0 flex-1 truncate text-ink">{file.name}</span>
                    <span className="shrink-0 text-xs text-ink-soft">
                      {formatBytes(file.size)}
                    </span>
                    {phase === 'idle' && (
                      <button
                        type="button"
                        onClick={() => removeFile(index)}
                        aria-label={`Remove ${file.name}`}
                        className="shrink-0 text-ink-soft hover:text-danger"
                      >
                        <X size={14} />
                      </button>
                    )}
                  </li>
                ))}
              </ul>
            )}

            {error && <p className="mt-3 text-sm text-danger">{error}</p>}

            {phase === 'uploading' && (
              <div className="mt-4">
                <div className="h-1.5 w-full overflow-hidden rounded-full bg-app-bg">
                  <div
                    className="h-full rounded-full bg-accent transition-all"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <p className="mt-2 text-center text-xs text-ink-soft">
                  Uploading and processing...
                </p>
              </div>
            )}

            <div className="mt-5 flex justify-end gap-2">
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg px-4 py-2 text-sm font-medium text-ink-soft hover:bg-app-bg"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={files.length === 0 || phase === 'uploading'}
                onClick={handleUpload}
                className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
              >
                {phase === 'uploading' ? 'Uploading...' : 'Upload'}
              </button>
            </div>
          </>
        )}

        {phase === 'done' && results && (
          <>
            <ul className="space-y-2">
              {results.map((doc) => (
                <li
                  key={doc.id}
                  className="flex items-center gap-2 rounded-lg border border-border px-3 py-2 text-sm"
                >
                  {doc.status === 'indexed' ? (
                    <CheckCircle2 size={16} className="shrink-0 text-success" />
                  ) : (
                    <XCircle size={16} className="shrink-0 text-danger" />
                  )}
                  <span className="min-w-0 flex-1 truncate text-ink">{doc.filename}</span>
                  <span
                    className={`shrink-0 text-xs font-medium ${
                      doc.status === 'indexed' ? 'text-success' : 'text-danger'
                    }`}
                  >
                    {doc.status === 'indexed' ? 'Indexed' : 'Failed'}
                  </span>
                </li>
              ))}
            </ul>
            <div className="mt-5 flex justify-end">
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover"
              >
                Done
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
