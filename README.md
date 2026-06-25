# University Knowledge Search

Учебный проект интеллектуальной поисковой системы по внутренней базе знаний университета.

## Реализовано

- регистрация и авторизация по логину и паролю без ролей;
- Bearer-токен с HMAC-подписью и сроком действия;
- загрузка PDF и DOCX до 20 МБ;
- извлечение текста через `pdfplumber` и `python-docx`;
- чанки по 1000 символов с перекрытием 100 символов;
- полнотекстовый поиск в Elasticsearch с русским анализатором;
- подсветка совпадений, релевантность и пагинация;
- PostgreSQL для документов и истории запросов;
- Redis-кеш на 5 минут;
- React + JavaScript + Vite, без TypeScript;
- Docker Compose, Swagger, GitHub Actions, Prometheus и Grafana;
- pytest, Playwright, Locust и Precision@3.

## Быстрый запуск

### Windows PowerShell

```powershell
Copy-Item .env.example .env
docker compose up --build -d
```

### Linux/macOS

```bash
cp .env.example .env
docker compose up --build -d
```

Откройте `http://localhost:3000`.

Демонстрационная учётная запись из `.env.example` (можно также зарегистрировать новую):

```text
Логин: student
Пароль: practice2026
```

Перед публикацией обязательно измените `AUTH_PASSWORD` и `AUTH_SECRET_KEY` в `.env`.

## Адреса сервисов

| Сервис | Адрес |
|---|---|
| Веб-интерфейс | http://localhost:3000 |
| Swagger UI | http://localhost:8000/docs |
| Healthcheck | http://localhost:8000/api/v1/health |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3001 |

## Как работают регистрация и авторизация

1. Новый пользователь открывает вкладку «Регистрация» и задаёт логин и пароль.
2. Frontend отправляет `POST /api/v1/auth/register`.
3. Backend проверяет уникальность логина, хеширует пароль через PBKDF2-SHA256 с индивидуальной солью и сохраняет пользователя в PostgreSQL.
4. После регистрации сервер сразу выдаёт подписанный Bearer-токен.
5. При обычном входе `POST /api/v1/auth/login` проверяет пароль по сохранённому хешу.
6. Frontend хранит токен в `localStorage` и добавляет `Authorization: Bearer ...` к защищённым запросам.
7. Загрузка документов, список документов, поиск и история требуют токен.
8. `/health`, `/docs`, `/metrics`, `/auth/login` и `/auth/register` остаются публичными.
9. Кнопка «Выйти» удаляет токен из браузера.

Схема остаётся упрощённой: у всех зарегистрированных пользователей одинаковые права, ролей и восстановления пароля нет. Документы и поисковая база общие для всех пользователей.

## Переменные авторизации

```env
# Необязательная демонстрационная учётная запись, создаваемая при первом запуске
AUTH_USERNAME=student
AUTH_PASSWORD=practice2026

# Подпись и срок действия токенов
AUTH_SECRET_KEY=replace-with-a-long-random-secret
AUTH_TOKEN_TTL_MINUTES=480
```

## Проверка API через curl

Зарегистрироваться:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"new_student","password":"securepass2026"}'
```

Успешная регистрация возвращает `201 Created` и токен. Повторный логин даёт `409 Conflict`.

Получить токен:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"practice2026"}'
```

Ответ:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "expires_in": 28800,
  "username": "student"
}
```

Защищённый запрос:

```bash
curl "http://localhost:8000/api/v1/documents?page=1&size=20" \
  -H "Authorization: Bearer ВАШ_ТОКЕН"
```

В Swagger нажмите **Authorize** и вставьте только значение токена.

## Как работает загрузка и поиск

1. После входа пользователь загружает PDF/DOCX.
2. FastAPI проверяет формат, размер и содержимое.
3. Метаданные сохраняются в PostgreSQL.
4. Текст извлекается, делится на чанки и индексируется в Elasticsearch.
5. Поиск сначала проверяет Redis.
6. При cache miss выполняется поиск в Elasticsearch.
7. Запрос сохраняется в историю, а результаты отображаются карточками.

## Полезные команды

```bash
docker compose ps
docker compose logs -f app
docker compose down
docker compose down -v
```

Полная пересборка:

```bash
docker compose down --remove-orphans
docker compose build --no-cache
docker compose up -d
```

## Тесты

Backend:

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
ruff check app tests
```

Frontend:

```bash
cd frontend
npm ci
npm run lint
npm run build
```

E2E:

```bash
cd e2e
npm ci
npx playwright install chromium
npm test
```

E2E-тест автоматически входит с логином и паролем из переменных окружения либо использует демонстрационные значения.

## Структура

```text
backend/       FastAPI, PostgreSQL, Elasticsearch, Redis, users/auth
frontend/      React + JavaScript + Vite + Nginx
e2e/           Playwright на JavaScript
load-tests/    Locust с авторизацией
monitoring/    Prometheus и Grafana
docs/          документация
docker-compose.yml
.env.example
init.sh
```

Подробности: `docs/ARCHITECTURE.md`, `docs/API_CONTRACT.md`, `docs/USER_GUIDE.md`.
