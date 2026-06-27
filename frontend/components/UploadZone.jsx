import { useRef, useState } from 'react'
import { uploadDocument } from '../services/api'

const MAX_SIZE = 20 * 1024 * 1024

function makeId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

export function UploadZone({ onUploaded }) {
  const inputRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)
  const [items, setItems] = useState([])

  const patchItem = (id, patch) => {
    setItems((current) => current.map((item) => (item.id === id ? { ...item, ...patch } : item)))
  }

  const processFiles = async (files) => {
    const accepted = files.filter((file) => {
      const extension = file.name.toLowerCase().split('.').pop()
      return (extension === 'pdf' || extension === 'docx') && file.size <= MAX_SIZE
    })

    const rejected = files.filter((file) => !accepted.includes(file))
    const rejectedItems = rejected.map((file) => ({
      id: makeId(),
      fileName: file.name,
      progress: 0,
      state: 'error',
      error: 'Допустимы PDF/DOCX размером до 20 МБ',
    }))

    const newItems = accepted.map((file) => ({
      id: makeId(),
      fileName: file.name,
      progress: 0,
      state: 'uploading',
    }))
    setItems((current) => [...newItems, ...rejectedItems, ...current].slice(0, 20))

    await Promise.all(
      accepted.map(async (file, index) => {
        const item = newItems[index]
        try {
          await uploadDocument(file, (progress) => {
            patchItem(item.id, {
              progress: progress < 100 ? progress : 90,
              state: progress < 100 ? 'uploading' : 'indexing',
            })
          })
          patchItem(item.id, { progress: 100, state: 'ready' })
          onUploaded()
        } catch (error) {
          patchItem(item.id, {
            progress: 100,
            state: 'error',
            error: error instanceof Error ? error.message : 'Ошибка загрузки',
          })
        }
      }),
    )
  }

  const handleFiles = (fileList) => {
    if (!fileList?.length) return
    void processFiles(Array.from(fileList))
  }

  return (
    <section className="panel" aria-labelledby="upload-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Шаг 1</p>
          <h2 id="upload-title">Загрузите документы</h2>
        </div>
        <span className="muted">PDF или DOCX, до 20 МБ</span>
      </div>

      <button
        className={`drop-zone ${isDragging ? 'drop-zone--active' : ''}`}
        type="button"
        onClick={() => inputRef.current?.click()}
        onDragEnter={(event) => {
          event.preventDefault()
          setIsDragging(true)
        }}
        onDragOver={(event) => event.preventDefault()}
        onDragLeave={(event) => {
          event.preventDefault()
          setIsDragging(false)
        }}
        onDrop={(event) => {
          event.preventDefault()
          setIsDragging(false)
          handleFiles(event.dataTransfer.files)
        }}
      >
        <strong>Перетащите файлы сюда</strong>
        <span>или нажмите, чтобы выбрать несколько файлов</span>
      </button>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx"
        multiple
        hidden
        onChange={(event) => handleFiles(event.target.files)}
      />

      {items.length > 0 && (
        <div className="upload-list" aria-live="polite">
          {items.map((item) => (
            <div className="upload-row" key={item.id}>
              <div className="upload-row__title">
                <span>{item.fileName}</span>
                <small>
                  {item.state === 'uploading' && 'Загрузка...'}
                  {item.state === 'indexing' && 'Индексация...'}
                  {item.state === 'ready' && 'Готово'}
                  {item.state === 'error' && (item.error ?? 'Ошибка')}
                </small>
              </div>
              <div className="progress" aria-label={`Прогресс ${item.fileName}`}>
                <span
                  className={item.state === 'error' ? 'progress__bar progress__bar--error' : 'progress__bar'}
                  style={{ width: `${item.progress}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
