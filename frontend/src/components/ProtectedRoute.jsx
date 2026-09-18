import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Layout from './Layout'

export default function ProtectedRoute({ children, adminOnly = false }) {
  const { user, loading, isAdmin } = useAuth()

  if (loading) {
    return <div className="flex items-center justify-center h-screen text-ink-soft">Chargement...</div>
  }
  if (!user) {
    return <Navigate to="/login" replace />
  }
  if (adminOnly && !isAdmin) {
    return <Navigate to="/chat" replace />
  }
  return <Layout>{children}</Layout>
}
