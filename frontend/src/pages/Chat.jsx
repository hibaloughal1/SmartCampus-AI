import React, { useState, useRef, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Send, FileText, Clock } from 'lucide-react'
import { sendMessage, getConversation } from '../services/chatService'

export default function Chat() {
  const [searchParams] = useSearchParams()
  const initialConvId = searchParams.get('conversation')

  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [conversationId, setConversationId] = useState(initialConvId || null)
  const [sending, setSending] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    if (initialConvId) {
      getConversation(initialConvId).then((conv) => {
        setConversationId(conv.id)
        setMessages(conv.messages.map((m) => ({
          role: m.role, content: m.content,
          sources: m.sources ? JSON.parse(m.sources) : [],
        })))
      })
    }
  }, [initialConvId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSend(e) {
    e.preventDefault()
    if (!input.trim() || sending) return

    const question = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: question, sources: [] }])
    setSending(true)

    try {
      const data = await sendMessage(question, conversationId)
      setConversationId(data.conversation_id)
      setMessages((prev) => [...prev, {
        role: 'assistant', content: data.message, sources: data.sources,
        responseTime: data.response_time_ms,
      }])
    } catch (err) {
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: "Une erreur est survenue lors du traitement de votre question.",
        sources: [],
      }])
    } finally {
      setSending(false)
    }
  }

  const suggestions = [
    'Résume le chapitre 3',
    'Explique les réseaux de neurones',
    'Génère un quiz sur ce cours',
    'Compare Random Forest et XGBoost',
  ]

  return (
    <div className="flex flex-col h-screen">
      <header className="border-b border-sage-dark px-8 py-5 bg-white">
        <h1 className="font-display text-2xl font-semibold">Assistant conversationnel</h1>
        <p className="text-sm text-ink-soft">Posez une question, l'assistant répond à partir des documents officiels</p>
      </header>

      <div className="flex-1 overflow-y-auto px-8 py-6 space-y-6">
        {messages.length === 0 && (
          <div className="max-w-2xl mx-auto mt-12 text-center">
            <p className="text-ink-soft mb-4">Essayez l'une de ces questions :</p>
            <div className="grid grid-cols-2 gap-3">
              {suggestions.map((s) => (
                <button key={s} onClick={() => setInput(s)}
                  className="card p-4 text-sm text-left hover:border-amber transition-colors">
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`max-w-3xl mx-auto ${m.role === 'user' ? 'flex justify-end' : ''}`}>
            <div className={`rounded-lg px-4 py-3 ${
              m.role === 'user' ? 'bg-ink text-paper max-w-lg' : 'card max-w-2xl'
            }`}>
              <p className="whitespace-pre-wrap text-sm leading-relaxed">{m.content}</p>

              {m.sources && m.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-sage-dark/50 flex flex-wrap gap-2">
                  {m.sources.map((s, idx) => (
                    <span key={idx} className="citation-badge" title={s.chunk_content}>
                      <FileText size={12} /> {s.document_title}
                    </span>
                  ))}
                </div>
              )}
              {m.responseTime && (
                <div className="mt-2 flex items-center gap-1 text-xs text-ink-soft">
                  <Clock size={12} /> {(m.responseTime / 1000).toFixed(1)}s
                </div>
              )}
            </div>
          </div>
        ))}

        {sending && (
          <div className="max-w-3xl mx-auto">
            <div className="card px-4 py-3 max-w-2xl inline-flex items-center gap-2 text-ink-soft text-sm">
              <span className="animate-pulse">L'assistant réfléchit...</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSend} className="border-t border-sage-dark bg-white px-8 py-4">
        <div className="max-w-3xl mx-auto flex gap-3">
          <input
            value={input} onChange={(e) => setInput(e.target.value)}
            placeholder="Posez votre question sur vos cours..."
            className="input-field flex-1"
          />
          <button type="submit" disabled={sending || !input.trim()} className="btn-amber flex items-center gap-2">
            <Send size={16} /> Envoyer
          </button>
        </div>
      </form>
    </div>
  )
}
