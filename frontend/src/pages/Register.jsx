import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { GraduationCap } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register(fullName, email, password)
      navigate('/chat')
    } catch (err) {
      setError(err.response?.data?.detail || 'Échec de la création du compte')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-sage px-4">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center mb-8">
          <GraduationCap className="text-amber mb-2" size={40} />
          <h1 className="font-display text-3xl font-semibold text-ink">SmartCampus AI</h1>
        </div>

        <form onSubmit={handleSubmit} className="card p-8 space-y-4">
          <h2 className="font-display text-xl font-semibold mb-2">Créer un compte</h2>

          {error && (
            <div className="bg-amber-soft border border-amber/30 text-amber text-sm rounded-md px-3 py-2">
              {error}
            </div>
          )}

          <div>
            <label className="text-sm font-medium text-ink-soft mb-1 block">Nom complet</label>
            <input required value={fullName} onChange={(e) => setFullName(e.target.value)} className="input-field" placeholder="Nom et prénom" />
          </div>
          <div>
            <label className="text-sm font-medium text-ink-soft mb-1 block">Email</label>
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="input-field" placeholder="etudiant@universite.ma" />
          </div>
          <div>
            <label className="text-sm font-medium text-ink-soft mb-1 block">Mot de passe</label>
            <input type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} className="input-field" placeholder="8 caractères minimum" />
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? 'Création...' : 'Créer mon compte'}
          </button>

          <p className="text-sm text-center text-ink-soft pt-2">
            Déjà inscrit ?{' '}
            <Link to="/login" className="text-amber font-medium hover:underline">Se connecter</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
