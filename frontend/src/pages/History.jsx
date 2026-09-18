import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { MessageSquare, Trash2 } from 'lucide-react'
import { listConversations, deleteConversation } from '../services/chatService'

export default function History() {
  const [conversations, setConversations] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => { load() }, [])

  async function load() {
    setLoading(true)
    const data = await listConversations()
    setConversations(data)
    setLoading(false)
  }

  async function handleDelete(id) {
    await deleteConversation(id)
    load()
  }

  return (
    <div className="px-8 py-6">
      <h1 className="font-display text-2xl font-semibold mb-1">Historique des conversations</h1>
      <p className="text-sm text-ink-soft mb-6">Retrouvez vos anciennes discussions avec l'assistant</p>

      {loading ? (
        <p className="text-ink-soft">Chargement...</p>
      ) : conversations.length === 0 ? (
        <div className="card p-8 text-center text-ink-soft">Aucune conversation pour le moment.</div>
      ) : (
        <div className="space-y-2 max-w-2xl">
          {conversations.map((c) => (
            <div key={c.id} className="card p-4 flex items-center justify-between hover:border-amber transition-colors">
              <Link to={`/chat?conversation=${c.id}`} className="flex items-center gap-3 flex-1">
                <MessageSquare size={18} className="text-amber" />
                <div>
                  <p className="font-medium text-sm">{c.title}</p>
                  <p className="text-xs text-ink-soft">{new Date(c.updated_at).toLocaleString('fr-FR')}</p>
                </div>
              </Link>
              <button onClick={() => handleDelete(c.id)} className="text-ink-soft hover:text-amber p-2">
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
