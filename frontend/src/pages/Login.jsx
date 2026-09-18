import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { GraduationCap } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/chat')
    } catch (err) {
      setError(err.response?.data?.detail || 'Échec de la connexion')
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
          <p className="text-ink-soft text-sm mt-1">Votre assistant universitaire intelligent</p>
        </div>

        <form onSubmit={handleSubmit} className="card p-8 space-y-4">
          <h2 className="font-display text-xl font-semibold mb-2">Connexion</h2>

          {error && (
            <div className="bg-amber-soft border border-amber/30 text-amber text-sm rounded-md px-3 py-2">
              {error}
            </div>
          )}

          <div>
            <label className="text-sm font-medium text-ink-soft mb-1 block">Email</label>
            <input
              type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
              className="input-field" placeholder="etudiant@universite.ma"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-ink-soft mb-1 block">Mot de passe</label>
            <input
              type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
              className="input-field" placeholder="••••••••"
            />
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? 'Connexion...' : 'Se connecter'}
          </button>

          <p className="text-sm text-center text-ink-soft pt-2">
            Pas encore de compte ?{' '}
            <Link to="/register" className="text-amber font-medium hover:underline">Créer un compte</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
