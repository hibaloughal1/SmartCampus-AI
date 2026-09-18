import React from 'react'
import { NavLink } from 'react-router-dom'
import { MessageSquare, FileText, LayoutDashboard, History, Brain, Layers, LogOut, GraduationCap } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const linkClass = ({ isActive }) =>
  `flex items-center gap-3 px-4 py-2.5 rounded-md text-sm font-medium transition-colors ${
    isActive ? 'bg-ink text-paper' : 'text-ink-soft hover:bg-sage'
  }`

export default function Sidebar() {
  const { user, logout, isAdmin } = useAuth()

  return (
    <aside className="w-64 bg-white border-r border-sage-dark flex flex-col h-screen sticky top-0">
      <div className="px-5 py-6 border-b border-sage-dark">
        <div className="flex items-center gap-2">
          <GraduationCap className="text-amber" size={26} />
          <span className="font-display text-xl font-semibold tracking-tight">SmartCampus</span>
        </div>
        <p className="text-xs text-ink-soft mt-1 font-mono">assistant universitaire IA</p>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        <NavLink to="/chat" className={linkClass}>
          <MessageSquare size={18} /> Assistant
        </NavLink>
        <NavLink to="/history" className={linkClass}>
          <History size={18} /> Historique
        </NavLink>
        <NavLink to="/quiz" className={linkClass}>
          <Brain size={18} /> Quiz
        </NavLink>
        <NavLink to="/flashcards" className={linkClass}>
          <Layers size={18} /> Flashcards
        </NavLink>

        {isAdmin && (
          <>
            <div className="pt-4 pb-1 px-4 text-xs uppercase tracking-wide text-ink-soft font-mono">Administration</div>
            <NavLink to="/documents" className={linkClass}>
              <FileText size={18} /> Documents
            </NavLink>
            <NavLink to="/dashboard" className={linkClass}>
              <LayoutDashboard size={18} /> Tableau de bord
            </NavLink>
          </>
        )}
      </nav>

      <div className="px-4 py-4 border-t border-sage-dark">
        <p className="text-sm font-medium truncate">{user?.full_name}</p>
        <p className="text-xs text-ink-soft truncate">{user?.email}</p>
        <button onClick={logout} className="mt-3 flex items-center gap-2 text-sm text-ink-soft hover:text-amber transition-colors">
          <LogOut size={16} /> Déconnexion
        </button>
      </div>
    </aside>
  )
}
