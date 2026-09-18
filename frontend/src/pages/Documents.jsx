import React, { useEffect, useState, useRef } from 'react'
import { Upload, FileText, Trash2, CheckCircle2, Clock, XCircle } from 'lucide-react'
import { listDocuments, uploadDocument, deleteDocument } from '../services/documentService'

const statusConfig = {
  indexed: { icon: CheckCircle2, color: 'text-sage-deep', label: 'Indexé' },
  processing: { icon: Clock, color: 'text-amber', label: 'Traitement...' },
  pending: { icon: Clock, color: 'text-ink-soft', label: 'En attente' },
  failed: { icon: XCircle, color: 'text-amber', label: 'Échec' },
}

export default function Documents() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const fileInput = useRef(null)

  useEffect(() => { load() }, [])

  async function load() {
    setLoading(true)
    const data = await listDocuments()
    setDocuments(data)
    setLoading(false)
  }

  async function handleFileChange(e) {
    const file = e.target.files[0]
    if (!file) return
    setUploading(true)
    try {
      await uploadDocument(file)
      await load()
    } finally {
      setUploading(false)
      fileInput.current.value = ''
    }
  }

  async function handleDelete(id) {
    if (!confirm('Supprimer ce document et réindexer la base ?')) return
    await deleteDocument(id)
    load()
  }

  return (
    <div className="px-8 py-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-semibold mb-1">Gestion des documents</h1>
          <p className="text-sm text-ink-soft">Importez des cours, TD, TP au format PDF, DOCX, PPTX ou TXT</p>
        </div>
        <label className="btn-amber flex items-center gap-2 cursor-pointer">
          <Upload size={16} /> {uploading ? 'Envoi...' : 'Importer un document'}
          <input ref={fileInput} type="file" accept=".pdf,.docx,.pptx,.txt" className="hidden" onChange={handleFileChange} disabled={uploading} />
        </label>
      </div>

      {loading ? (
        <p className="text-ink-soft">Chargement...</p>
      ) : documents.length === 0 ? (
        <div className="card p-8 text-center text-ink-soft">Aucun document importé pour le moment.</div>
      ) : (
        <div className="card divide-y divide-sage-dark/50">
          {documents.map((d) => {
            const status = statusConfig[d.status] || statusConfig.pending
            const StatusIcon = status.icon
            return (
              <div key={d.id} className="flex items-center justify-between px-5 py-4">
                <div className="flex items-center gap-3">
                  <FileText size={20} className="text-amber" />
                  <div>
                    <p className="font-medium text-sm">{d.title}</p>
                    <p className="text-xs text-ink-soft font-mono">
                      {d.file_type.toUpperCase()} · {d.num_chunks} segments · {d.num_views} consultations
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className={`flex items-center gap-1 text-xs font-medium ${status.color}`}>
                    <StatusIcon size={14} /> {status.label}
                  </span>
                  <button onClick={() => handleDelete(d.id)} className="text-ink-soft hover:text-amber p-2">
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
