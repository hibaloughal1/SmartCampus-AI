import React, { useEffect, useState } from 'react'
import { Brain, CheckCircle2, XCircle } from 'lucide-react'
import { generateQuiz, listQuizzes } from '../services/quizService'
import { listDocuments } from '../services/documentService'

export default function Quiz() {
  const [quizzes, setQuizzes] = useState([])
  const [documents, setDocuments] = useState([])
  const [documentId, setDocumentId] = useState('')
  const [topic, setTopic] = useState('')
  const [numQuestions, setNumQuestions] = useState(5)
  const [generating, setGenerating] = useState(false)
  const [activeQuiz, setActiveQuiz] = useState(null)
  const [answers, setAnswers] = useState({})
  const [submitted, setSubmitted] = useState(false)

  useEffect(() => {
    listQuizzes().then(setQuizzes)
    listDocuments().then(setDocuments).catch(() => {})
  }, [])

  async function handleGenerate(e) {
    e.preventDefault()
    setGenerating(true)
    try {
      const quiz = await generateQuiz(documentId || null, topic || null, Number(numQuestions))
      setQuizzes((prev) => [quiz, ...prev])
      setActiveQuiz(quiz)
      setAnswers({})
      setSubmitted(false)
    } finally {
      setGenerating(false)
    }
  }

  function selectAnswer(questionId, option) {
    if (submitted) return
    setAnswers((prev) => ({ ...prev, [questionId]: option }))
  }

  const score = activeQuiz
    ? activeQuiz.questions.filter((q) => answers[q.id] === q.correct_option).length
    : 0

  return (
    <div className="px-8 py-6">
      <h1 className="font-display text-2xl font-semibold mb-1">Génération de quiz</h1>
      <p className="text-sm text-ink-soft mb-6">Créez un QCM à partir d'un document ou d'un thème pour réviser</p>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-1 space-y-4">
          <form onSubmit={handleGenerate} className="card p-5 space-y-3">
            <h2 className="font-display font-semibold flex items-center gap-2"><Brain size={18} className="text-amber" /> Nouveau quiz</h2>
            <div>
              <label className="text-xs font-medium text-ink-soft block mb-1">Document (optionnel)</label>
              <select value={documentId} onChange={(e) => setDocumentId(e.target.value)} className="input-field text-sm">
                <option value="">Aucun document spécifique</option>
                {documents.map((d) => <option key={d.id} value={d.id}>{d.title}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-ink-soft block mb-1">Thème</label>
              <input value={topic} onChange={(e) => setTopic(e.target.value)} className="input-field text-sm" placeholder="ex: Réseaux de neurones" />
            </div>
            <div>
              <label className="text-xs font-medium text-ink-soft block mb-1">Nombre de questions</label>
              <input type="number" min={3} max={15} value={numQuestions} onChange={(e) => setNumQuestions(e.target.value)} className="input-field text-sm" />
            </div>
            <button type="submit" disabled={generating} className="btn-amber w-full text-sm">
              {generating ? 'Génération...' : 'Générer le quiz'}
            </button>
          </form>

          <div className="card p-4">
            <h3 className="text-sm font-medium text-ink-soft mb-2">Mes quiz</h3>
            <div className="space-y-1 max-h-64 overflow-y-auto">
              {quizzes.map((q) => (
                <button key={q.id} onClick={() => { setActiveQuiz(q); setAnswers({}); setSubmitted(false) }}
                  className="w-full text-left text-sm px-2 py-1.5 rounded hover:bg-sage truncate">
                  {q.title}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="col-span-2">
          {!activeQuiz ? (
            <div className="card p-8 text-center text-ink-soft h-full flex items-center justify-center">
              Sélectionnez ou générez un quiz pour commencer
            </div>
          ) : (
            <div className="card p-6 space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="font-display text-lg font-semibold">{activeQuiz.title}</h2>
                {submitted && (
                  <span className="citation-badge">Score : {score}/{activeQuiz.questions.length}</span>
                )}
              </div>

              {activeQuiz.questions.map((q, idx) => (
                <div key={q.id} className="border-b border-sage-dark/50 pb-5 last:border-0">
                  <p className="font-medium mb-3">{idx + 1}. {q.question}</p>
                  <div className="space-y-2">
                    {['A', 'B', 'C', 'D'].map((opt) => {
                      const optionText = q[`option_${opt.toLowerCase()}`]
                      const isSelected = answers[q.id] === opt
                      const isCorrect = q.correct_option === opt
                      let style = 'border-sage-dark hover:border-amber'
                      if (submitted) {
                        if (isCorrect) style = 'border-sage-deep bg-sage'
                        else if (isSelected && !isCorrect) style = 'border-amber bg-amber-soft'
                      } else if (isSelected) {
                        style = 'border-ink bg-sage'
                      }
                      return (
                        <button key={opt} onClick={() => selectAnswer(q.id, opt)}
                          className={`w-full text-left px-3 py-2 rounded-md border text-sm flex items-center justify-between ${style}`}>
                          <span><span className="font-mono text-xs text-ink-soft mr-2">{opt}</span>{optionText}</span>
                          {submitted && isCorrect && <CheckCircle2 size={16} className="text-sage-deep" />}
                          {submitted && isSelected && !isCorrect && <XCircle size={16} className="text-amber" />}
                        </button>
                      )
                    })}
                  </div>
                  {submitted && q.explanation && (
                    <p className="text-xs text-ink-soft mt-2 italic">{q.explanation}</p>
                  )}
                </div>
              ))}

              {!submitted && (
                <button onClick={() => setSubmitted(true)} className="btn-primary">Valider mes réponses</button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
