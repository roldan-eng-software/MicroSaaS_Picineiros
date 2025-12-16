import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

import { getMe, initFromRefresh, login as apiLogin, logout as apiLogout } from './api'

type User = {
  id: string
  email: string
  nome: string
  telefone: string
  is_active: boolean
}

type AuthContextValue = {
  loading: boolean
  accessToken: string | null
  user: User | null
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refresh: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true)
  const [accessToken, setAccessToken] = useState<string | null>(() => localStorage.getItem('access_token'))
  const [user, setUser] = useState<User | null>(null)

  const syncMe = useCallback(async () => {
    if (!localStorage.getItem('access_token')) {
      setUser(null)
      return
    }
    const me = await getMe()
    setUser(me)
  }, [])

  const refresh = useCallback(async () => {
    const token = await initFromRefresh()
    localStorage.setItem('access_token', token)
    setAccessToken(token)
    await syncMe()
  }, [syncMe])

  const login = useCallback(
    async (email: string, password: string) => {
      const token = await apiLogin(email, password)
      localStorage.setItem('access_token', token)
      setAccessToken(token)
      await syncMe()
    },
    [syncMe],
  )

  const logout = useCallback(async () => {
    await apiLogout().catch(() => undefined)
    localStorage.removeItem('access_token')
    setAccessToken(null)
    setUser(null)
  }, [])

  useEffect(() => {
    let cancelled = false

    const run = async () => {
      try {
        await refresh()
      } catch {
        if (!cancelled) {
          localStorage.removeItem('access_token')
          setAccessToken(null)
          setUser(null)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    run()

    return () => {
      cancelled = true
    }
  }, [refresh])

  const value = useMemo<AuthContextValue>(
    () => ({
      loading,
      accessToken,
      user,
      login,
      logout,
      refresh,
    }),
    [loading, accessToken, user, login, logout, refresh],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
