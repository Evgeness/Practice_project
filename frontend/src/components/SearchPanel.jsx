import { useEffect, useState } from 'react'
import { searchDocuments } from '../services/api'
import { SearchResults } from './SearchResults'

export function SearchPanel() {
  const [query, setQuery] = useState('')
  const [submittedQuery, setSubmittedQuery] = useState('')
  const [page, setPage] = useState(1)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const runSearch = async (searchQuery, targetPage) => {
    if (!searchQuery.trim()) return
    setLoading(true)
    setError('')
    try {
      const data = await searchDocuments(searchQuery.trim(), targetPage, 10)
      setResult(data)
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Ошибка поиска')
    } finally {
      setLoading(false)
    }
  }

  const submit = (event) => {
    event.preventDefault()
    const normalized = query.trim()
    if (!normalized) return
    setSubmittedQuery(normalized)
    setPage(1)
    void runSearch(normalized, 1)
  }

  useEffect(() => {
    if (!submittedQuery || page === 1) return
    void runSearch(submittedQuery, page)
  }, [page, submittedQuery])

  const totalPages = result ? Math.max(1, Math.ceil(result.total / result.size)) : 1

  return (
    <section className="panel panel--search" aria-labelledby="search-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Шаг 2</p>
          <h2 id="search-title">Найдите информацию</h2>
        </div>
        {result?.cached && <span className="cache-badge">Ответ из кеша</span>}
      </div>

      <form className="search-form" onSubmit={submit}>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Например: требования к курсовой работе"
          aria-label="Поисковый запрос"
          maxLength={200}
        />
        <button type="submit" disabled={loading || !query.trim()}>
          {loading ? 'Ищем...' : 'Найти'}
        </button>
      </form>

      {error && <p className="error-banner">{error}</p>}
      {result && <SearchResults response={result} query={submittedQuery} />}

      {result && result.total > result.size && (
        <nav className="pagination" aria-label="Страницы результатов">
          <button type="button" onClick={() => setPage((value) => Math.max(1, value - 1))} disabled={page === 1 || loading}>
            Назад
          </button>
          <span>Страница {page} из {totalPages}</span>
          <button type="button" onClick={() => setPage((value) => Math.min(totalPages, value + 1))} disabled={page >= totalPages || loading}>
            Вперёд
          </button>
        </nav>
      )}
    </section>
  )
}
