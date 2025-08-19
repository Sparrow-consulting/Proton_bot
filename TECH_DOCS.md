# Техническая документация Proton_bot

## Описание проекта
Proton_bot - Telegram-бот с FastAPI для отправки уведомлений. Интегрируется с внешними системами через REST API.

## Архитектура
- **Telegram Bot** (aiogram 3.4.1) - пользовательский интерфейс
- **FastAPI** (0.111.0) - REST API для интеграции
- **Python 3.11+** - основной язык

## Основные компоненты

### 1. Telegram Bot
- Команды: `/start`, `/id`, `/stop`
- Обработка контактов пользователей
- Регистрация через внешний API

### 2. FastAPI Endpoint
- `POST /notify` - отправка уведомлений
- Аутентификация по API ключу
- Поддержка HTML и инлайн-кнопок

### 3. Конфигурация
```env
BOT_TOKEN=telegram_bot_token
API_URL=external_api_url
NOTIFY_SECRET=api_secret_key
```

## Развертывание

### Локально
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Docker
```bash
docker build -t tg-bot:latest .
docker run -d --name tg-bot --env-file .env -p 8000:8000 tg-bot:latest
```

## API интеграция

### Отправка уведомления
```bash
curl -X POST "http://localhost:8000/notify" \
  -H "x-api-key: your_secret" \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": 123, "text": "Сообщение", "url": "https://example.com"}'
```

### Внешние API endpoints
- `POST {API_URL}/telegram/register` - регистрация
- `POST {API_URL}/telegram/unsubscribe` - отписка

## Безопасность
- Валидация API ключей
- Проверка формата номеров телефонов
- Санитизация HTML-контента

## Мониторинг
- Логирование всех операций
- Обработка ошибок
- Статус отправки уведомлений
