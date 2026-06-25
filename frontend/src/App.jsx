import { useCallback, useEffect, useState } from 'react'
import { AuthPage } from './pages/AuthPage'
import { HomePage } from './pages/HomePage'
import {
  clearAccessToken,
  getAccessToken,
  getCurrentUser,
  listDocuments,
  login,
  register,
} from './services/api'

export default function App() {
  const [authState, setAuthState] = useState(getAccessToken() ? 'checking' : 'anonymous')
  const [username, setUsername] = useState('')
  const [documents, setDocuments] = useState([])
  const [loadingDocuments, setLoadingDocuments] = useState(false)

  const logout = useCallback(() => {
    clearAccessToken()
    setUsername('')
    setDocuments([])
    setAuthState('anonymous')
  }, [])

  useEffect(() => {
    const handleUnauthorized = () => logout()
    window.addEventListener('auth:unauthorized', handleUnauthorized)
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized)
  }, [logout])

  useEffect(() => {
    if (authState !== 'checking') return
    getCurrentUser()
      .then((user) => {
        setUsername(user.username)
        setAuthState('authenticated')
      })
      .catch(() => logout())
  }, [authState, logout])

  const refreshDocuments = useCallback(async () => {
    if (authState !== 'authenticated') return
    setLoadingDocuments(true)
    try {
      const data = await listDocuments()
      setDocuments(data.items)
    } finally {
      setLoadingDocuments(false)
    }
  }, [authState])

  useEffect(() => {
    void refreshDocuments()
  }, [refreshDocuments])

  const handleLogin = async (submittedUsername, password) => {
    const result = await login(submittedUsername, password)
    setUsername(result.username)
    setAuthState('authenticated')
  }

  const handleRegister = async (submittedUsername, password) => {
    const result = await register(submittedUsername, password)
    setUsername(result.username)
    setAuthState('authenticated')
  }

  if (authState === 'checking') {
    return <div className="auth-loading">Проверка авторизации...</div>
  }

  if (authState !== 'authenticated') {
    return <AuthPage onLogin={handleLogin} onRegister={handleRegister} />
  }

  return (
    <HomePage
      username={username}
      onLogout={logout}
      documents={documents}
      loadingDocuments={loadingDocuments}
      onUploaded={refreshDocuments}
    />
  )
}
