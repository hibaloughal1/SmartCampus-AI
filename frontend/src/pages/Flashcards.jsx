import React, { useEffect, useState } from 'react'
import { Layers, RotateCw, ChevronLeft, ChevronRight } from 'lucide-react'
import { generateFlashcards, listFlashcardSets } from '../services/quizService'
import { listDocuments } from '../services/documentService'

export default function Flashcards() {
  const [sets, setSets] = useState([])
  const [documents, setDocuments] = useState([])
  const [documentId, setDocumentId] = useState('')
  const [topic, setTopic] = useState('')
  const [numCards, setNumCards] = useState(10)
  const [generating, setGenerating] = useState(false)
  const [activeSet, setActiveSet] = useState(null)
  const [index, setIndex] = useState(0)
  const [flipped, setFlipped] = useState(false)

  useEffect(() => {
    listFlashcardSets().then(setSets)
    listDocuments().then(setDocuments).catch(() => {})
  }, [])

  async function handleGenerate(e) {
    e.preventDefault()
    setGenerating(true)
    try {
      const fset = await generateFlashcards(documentId || null, topic || null, Number(numCards))
      setSets((prev) => [fset, ...prev])
      openSet(fset)
    } finally {
      setGenerating(false)
    }
  }

  function openSet(fset) {
    setActiveSet(fset)
    setIndex(0)
    setFlipped(false)
  }

  function next() {
    setFlipped(false)
    setIndex((i) => Math.min(i + 1, activeSet.flashcards.length - 1))
  }
  function prev() {
    setFlipped(false)
    setIndex((i) => Math.max(i - 1, 0))
  }

  const card = activeSet?.flashcards[index]

  return (
    <div className="px-8 py-6">
      <h1 className="font-display text-2xl font-semibold mb-1">Fiches de révision</h1>
      <p className="text-sm text-ink-soft mb-6">Générez des flashcards à partir de vos cours pour réviser efficacement</p>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-1 space-y-4">
          <form onSubmit={handleGenerate} className="card p-5 space-y-3">
            <h2 className="font-display font-semibold flex items-center gap-2"><Layers size={18} className="text-amber" /> Nouvelles fiches</h2>
            <div>
              <label className="text-xs font-medium text-ink-soft block mb-1">Document (optionnel)</label>
              <select value={documentId} onChange={(e) => setDocumentId(e.target.value)} className="input-field text-sm">
                <option value="">Aucun document spécifique</option>
                {documents.map((d) => <option key={d.id} value={d.id}>{d.title}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-ink-soft block mb-1">Thème</label>
              <input value={topic} onChange={(e) => setTopic(e.target.value)} className="input-field text-sm" placeholder="ex: Surapprentissage" />
            </div>
            <div>
              <label className="text-xs font-medium text-ink-soft block mb-1">Nombre de fiches</label>
              <input type="number" min={5} max={30} value={numCards} onChange={(e) => setNumCards(e.target.value)} className="input-field text-sm" />
            </div>
            <button type="submit" disabled={generating} className="btn-amber w-full text-sm">
              {generating ? 'Génération...' : 'Générer les fiches'}
            </button>
          </form>

          <div className="card p-4">
            <h3 className="text-sm font-medium text-ink-soft mb-2">Mes fiches</h3>
            <div className="space-y-1 max-h-64 overflow-y-auto">
              {sets.map((s) => (
                <button key={s.id} onClick={() => openSet(s)} className="w-full text-left text-sm px-2 py-1.5 rounded hover:bg-sage truncate">
                  {s.title}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="col-span-2">
          {!activeSet ? (
            <div className="card p-8 text-center text-ink-soft h-full flex items-center justify-center">
              Sélectionnez ou générez des fiches pour commencer
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <p className="text-sm text-ink-soft mb-3 font-mono">{index + 1} / {activeSet.flashcards.length}</p>
              <button
                onClick={() => setFlipped((f) => !f)}
                className="card w-full max-w-md h-64 flex items-center justify-center p-8 text-center cursor-pointer hover:border-amber transition-colors"
              >
                <p className="text-lg font-display">{flipped ? card?.back : card?.front}</p>
              </button>
              <div className="flex items-center gap-4 mt-4">
                <button onClick={prev} disabled={index === 0} className="btn-secondary flex items-center gap-1 text-sm">
                  <ChevronLeft size={16} /> Précédent
                </button>
                <button onClick={() => setFlipped((f) => !f)} className="btn-secondary flex items-center gap-1 text-sm">
                  <RotateCw size={16} /> Retourner
                </button>
                <button onClick={next} disabled={index === activeSet.flashcards.length - 1} className="btn-secondary flex items-center gap-1 text-sm">
                  Suivant <ChevronRight size={16} />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
