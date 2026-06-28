function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} Б`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`
  return `${(bytes / 1024 / 1024).toFixed(1)} МБ`
}

function statusText(status) {
  if (status === 'ready') return 'Готово'
  if (status === 'processing') return 'Индексация'
  return 'Ошибка'
}

export function DocumentsList({ documents, loading }) {
  return (
    <section className="panel" aria-labelledby="documents-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">База знаний</p>
          <h2 id="documents-title">Загруженные документы</h2>
        </div>
        <span className="count-badge">{documents.length}</span>
      </div>

      {loading && <p className="muted">Загрузка списка...</p>}
      {!loading && documents.length === 0 && (
        <p className="empty-state">Документов пока нет. Загрузите первый файл.</p>
      )}
      {!loading && documents.length > 0 && (
        <div className="document-table-wrap">
          <table className="document-table">
            <thead>
              <tr>
                <th>Документ</th>
                <th>Дата</th>
                <th>Размер</th>
                <th>Статус</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((document) => (
                <tr key={document.id}>
                  <td>
                    <strong>{document.file_name}</strong>
                  </td>
                  <td>{new Date(document.uploaded_at).toLocaleString('ru-RU')}</td>
                  <td>{formatBytes(document.file_size)}</td>
                  <td>
                    <span className={`status status--${document.status}`}>
                      {statusText(document.status)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
