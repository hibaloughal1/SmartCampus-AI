import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { login as loginApi, register as registerApi, fetchCurrentUser } from '../services/authService'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('sc_user')
    return stored ? JSON.parse(stored) : null
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('sc_token')
    if (token) {
      fetchCurrentUser()
        .then((u) => {
          setUser(u)
          localStorage.setItem('sc_user', JSON.stringify(u))
        })
        .catch(() => {
          localStorage.removeItem('sc_token')
          localStorage.removeItem('sc_user')
          setUser(null)
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = useCallback(async (email, password) => {
    const data = await loginApi(email, password)
    localStorage.setItem('sc_token', data.access_token)
    localStorage.setItem('sc_user', JSON.stringify(data.user))
    setUser(data.user)
    return data.user
  }, [])

  const register = useCallback(async (fullName, email, password) => {
    await registerApi(fullName, email, password)
    return login(email, password)
  }, [login])

  const logout = useCallback(() => {
    localStorage.removeItem('sc_token')
    localStorage.removeItem('sc_user')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, isAdmin: user?.role === 'admin' }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
