import axios from 'axios'

const TOKEN_KEY = 'knowledge-search-access-token'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api/v1',
  timeout: 120_000,
})

export function getAccessToken() {
  return window.localStorage.getItem(TOKEN_KEY)
}

export function setAccessToken(token) {
  window.localStorage.setItem(TOKEN_KEY, token)
}

export function clearAccessToken() {
  window.localStorage.removeItem(TOKEN_KEY)
}

api.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isPublicAuthRequest =
      error.config?.url?.endsWith('/auth/login') ||
      error.config?.url?.endsWith('/auth/register')
    if (error.response?.status === 401 && !isPublicAuthRequest) {
      clearAccessToken()
      window.dispatchEvent(new Event('auth:unauthorized'))
    }
    return Promise.reject(error)
  },
)

export function getErrorMessage(error) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (error.code === 'ECONNABORTED') return 'Сервер не ответил вовремя'
  }
  return 'Произошла непредвиденная ошибка'
}

export async function login(username, password) {
  try {
    const response = await api.post('/auth/login', { username, password })
    setAccessToken(response.data.access_token)
    return response.data
  } catch (error) {
    throw new Error(getErrorMessage(error))
  }
}

export async function register(username, password) {
  try {
    const response = await api.post('/auth/register', { username, password })
    setAccessToken(response.data.access_token)
    return response.data
  } catch (error) {
    throw new Error(getErrorMessage(error))
  }
}

export async function getCurrentUser() {
  const response = await api.get('/auth/me')
  return response.data
}

export async function uploadDocument(file, onProgress) {
  const form = new FormData()
  form.append('file', file)
  try {
    const response = await api.post('/documents/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => {
        if (!event.total) return
        const progress = Math.min(100, Math.round((event.loaded * 100) / event.total))
        onProgress(progress)
      },
    })
    return response.data
  } catch (error) {
    throw new Error(getErrorMessage(error))
  }
}

export async function listDocuments() {
  const response = await api.get('/documents', { params: { page: 1, size: 100 } })
  return response.data
}

export async function searchDocuments(query, page = 1, size = 10) {
  try {
    const response = await api.get('/search', { params: { q: query, page, size } })
    return response.data
  } catch (error) {
    throw new Error(getErrorMessage(error))
  }
}
