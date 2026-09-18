import React, { useState } from 'react'
import { BookOpen, ChevronDown, ChevronUp } from 'lucide-react'

export default function SourceCitations({ sources }) {
  const [open, setOpen] = useState(false)
  if (!sources || sources.length === 0) return null

  return (
    <div className="mt-3">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 text-xs font-mono text-amber-dark hover:text-amber transition-colors"
      >
        <BookOpen size={14} />
        {sources.length} source{sources.length > 1 ? 's' : ''} citée{sources.length > 1 ? 's' : ''}
        {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>
      {open && (
        <div className="mt-2 space-y-2">
          {sources.map((s, i) => (
            <div key={i} className="bg-amber/5 border border-amber/20 rounded-md p-3">
              <div className="flex items-center justify-between mb-1">
                <span className="citation-tag">{s.document_title}</span>
                <span className="text-xs font-mono text-ink/40">score {s.score}</span>
              </div>
              <p className="text-sm text-ink/70 leading-relaxed">{s.chunk_content}...</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
