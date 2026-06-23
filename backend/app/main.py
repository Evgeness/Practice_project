import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Загружаем переменные из .env (если файл есть)
load_dotenv()

# Создаём экземпляр приложения
app = FastAPI(
    title="Knowledge Search API",
    version="1.0.0",
    description="Бэкенд для интеллектуальной поисковой системы",
)

# Настройка CORS (для разработки разрешаем все источники)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # В продакшене замените на конкретный домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ Модели данных (Pydantic) ------------------
class UploadResponse(BaseModel):
    id: str
    filename: str
    message: str

class PingResponse(BaseModel):
    status: str

# ------------------ Эндпоинты ------------------

@app.get("/ping", response_model=PingResponse)
async def health_check():
    """Проверка работоспособности сервиса."""
    return {"status": "ok"}

@app.post("/api/v1/documents/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Загрузка документа с валидацией формата и размера.
    Возвращает UUID загруженного файла.
    """
    # 1. Валидация расширения
    allowed_extensions = {".pdf", ".docx"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неподдерживаемый формат. Разрешены: {', '.join(allowed_extensions)}"
        )

    # 2. Валидация размера (читаем содержимое)
    content = await file.read()
    file_size = len(content)
    if file_size > 20 * 1024 * 1024:  # 20 МБ
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Размер файла превышает 20 МБ"
        )

    # 3. Генерация уникального идентификатора
    file_id = str(uuid.uuid4())

    # TODO: Здесь будет сохранение файла, извлечение текста, индексация в Elasticsearch
    # Пока возвращаем заглушку

    return UploadResponse(
        id=file_id,
        filename=file.filename,
        message="Файл успешно загружен (заглушка)"
    )

# ------------------ Точка входа для локального запуска ------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,          # Автоматический перезапуск при изменении кода
    )