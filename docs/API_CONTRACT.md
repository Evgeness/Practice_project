# Контракт API

Базовый префикс: `/api/v1`.

## Авторизация

### POST `/auth/register`

Публичный endpoint. Создаёт пользователя и сразу возвращает Bearer-токен.

```json
{
  "username": "new_student",
  "password": "securepass2026"
}
```

Ответ `201 Created`:

```json
{
  "access_token": "signed-token",
  "token_type": "bearer",
  "expires_in": 28800,
  "username": "new_student"
}
```

Ограничения: логин 3–50 символов; допустимы буквы, цифры, `.`, `-`, `_`; пароль минимум 8 символов. Ошибка `409` означает, что логин уже занят.

### POST `/auth/login`

Публичный endpoint. Принимает логин и пароль зарегистрированного пользователя:

```json
{
  "username": "student",
  "password": "practice2026"
}
```

Ответ `200 OK` имеет тот же формат токена. Ошибка `401` — неверный логин или пароль.

### GET `/auth/me`

Требует заголовок:

```text
Authorization: Bearer <access_token>
```

Ответ:

```json
{"username":"student"}
```

### Защищённые endpoints

Bearer-токен требуется для:

- `POST /documents/upload`;
- `GET /documents`;
- `GET /search`;
- `GET /search/history`;
- `GET /auth/me`.

При отсутствии, повреждении или истечении токена возвращается `401 Unauthorized`.

## POST `/documents/upload`

Загружает один PDF или DOCX. Запрос: `multipart/form-data`, поле `file`.

Успех: `201 Created`.

```json
{
  "id": "9b2e...",
  "file_name": "lecture.pdf",
  "file_type": "pdf",
  "file_size": 123456,
  "status": "ready",
  "chunks_count": 14,
  "error_message": null,
  "uploaded_at": "2026-06-23T10:00:00Z"
}
```

Ошибки: `400` — валидация/парсинг, `401` — нет авторизации, `500` — инфраструктура.

## GET `/documents`

Параметры: `page` от 1, `size` от 1 до 100.

## GET `/search`

Параметры: `q` — 1–200 символов, `page` от 1, `size` 1–50.

```json
{
  "query": "программная инженерия",
  "page": 1,
  "size": 10,
  "total": 4,
  "cached": false,
  "items": [
    {
      "chunk_id": "uuid:1",
      "document_id": "uuid",
      "file_name": "lecture.pdf",
      "page": 3,
      "text": "полный текст чанка",
      "highlight": "[[HIGHLIGHT]]программная[[/HIGHLIGHT]] инженерия",
      "score": 2.743
    }
  ]
}
```

## GET `/search/history`

Параметр `limit`: 1–100. Возвращает последние запросы.

## Публичные системные endpoints

- `GET /health` — состояние PostgreSQL, Elasticsearch и Redis;
- `GET /metrics` — метрики Prometheus;
- `/docs` — Swagger UI.
