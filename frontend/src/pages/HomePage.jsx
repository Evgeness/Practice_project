import { DocumentsList } from '../components/DocumentsList'
import { SearchPanel } from '../components/SearchPanel'
import { UploadZone } from '../components/UploadZone'

export function HomePage({ username, onLogout, documents, loadingDocuments, onUploaded }) {
  return (
    <div className="app-shell">
      <header className="hero">
        <div className="hero__content">
          <div className="hero__account">
            <span>
              Пользователь: <strong>{username}</strong>
            </span>
            <button type="button" onClick={onLogout}>
              Выйти
            </button>
          </div>
          <h1>Интеллектуальный поиск по базе знаний университета</h1>
          <p>
            Загружайте учебные материалы в PDF и DOCX, а затем находите нужные
            фрагменты с русскоязычным полнотекстовым поиском.
          </p>
        </div>
      </header>

      <main>
        <div className="grid-two">
          <UploadZone onUploaded={onUploaded} />
          <DocumentsList documents={documents} loading={loadingDocuments} />
        </div>
        <SearchPanel />
      </main>
    </div>
  )
}
