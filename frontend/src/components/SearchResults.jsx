const START = '[[HIGHLIGHT]]'
const END = '[[/HIGHLIGHT]]'

function renderHighlighted(value, query) {
  if (value.includes(START)) {
    const tokens = value.split(/(\[\[HIGHLIGHT\]\].*?\[\[\/HIGHLIGHT\]\])/g)
    return tokens.map((token, index) => {
      if (token.startsWith(START) && token.endsWith(END)) {
        return <mark key={index}>{token.slice(START.length, -END.length)}</mark>
      }
      return <span key={index}>{token}</span>
    })
  }

  const words = query.split(/\s+/).filter((word) => word.length > 1)
  if (!words.length) return [value]
  const escaped = words.map((word) => word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
  const pattern = new RegExp(`(${escaped.join('|')})`, 'gi')
  return value.split(pattern).map((part, index) =>
    words.some((word) => word.toLowerCase() === part.toLowerCase())
      ? <mark key={index}>{part}</mark>
      : <span key={index}>{part}</span>,
  )
}

export function SearchResults({ response, query }) {
  if (response.total === 0) {
    return (
      <p className="empty-state search-empty">
        По вашему запросу ничего не найдено. Попробуйте изменить формулировку.
      </p>
    )
  }

  return (
    <div className="results" aria-live="polite">
      <div className="results__summary">
        Найдено фрагментов: <strong>{response.total}</strong>
      </div>
      {response.items.map((item) => (
        <article className="result-card" key={item.chunk_id}>
          <header>
            <div>
              <h3>{item.file_name}</h3>
              <span>Страница {item.page}</span>
            </div>
            <span className="score">Релевантность {item.score.toFixed(2)}</span>
          </header>
          <p>{renderHighlighted(item.highlight ?? item.text.slice(0, 500), query)}</p>
        </article>
      ))}
    </div>
  )
}
