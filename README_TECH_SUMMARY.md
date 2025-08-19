# Краткая техническая сводка Proton_bot

## 🎯 Назначение
Telegram-бот с FastAPI для отправки уведомлений. Интегрируется с внешними системами через REST API.

## 🏗️ Архитектура
```
External API ←→ FastAPI (Port 8000) ←→ Telegram Bot
```

## 🚀 Быстрый старт

### Переменные окружения (.env)
```env
BOT_TOKEN=your_bot_token
API_URL=https://your-api.com/
NOTIFY_SECRET=your_secret_key
```

### Локальный запуск
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Docker
```bash
docker build -t proton-bot:latest .
docker run -d --name proton-bot --env-file .env -p 8000:8000 proton-bot:latest
```

## 📡 API Endpoints

### POST /notify
Отправка уведомлений пользователям
```bash
curl -X POST "http://localhost:8000/notify" \
  -H "x-api-key: your_secret" \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": 123, "text": "Сообщение", "url": "https://example.com"}'
```

## 🤖 Telegram Bot Commands
- `/start` - Регистрация
- `/id` - Показать Telegram ID
- `/stop` - Отписка

## 🔒 Безопасность
- API ключи для аутентификации
- Валидация номеров телефонов
- Санитизация HTML-контента

## 📊 Мониторинг
```bash
# Логи
docker logs proton-bot

# Статус
docker ps | grep proton-bot

# Статистика
docker stats proton-bot
```

## 📚 Полная документация
- `TECH_DOCS.md` - Краткая техническая документация
- `DETAILED_TECH_DOCS.md` - Детальная техническая документация

## 🛠️ Технологии
- Python 3.11+
- FastAPI 0.111.0
- aiogram 3.4.1
- uvicorn 0.29.0
- Docker

## 🔧 Устранение неполадок
1. Проверьте переменные окружения
2. Убедитесь в корректности BOT_TOKEN
3. Проверьте логи: `docker logs proton-bot`
4. Тестируйте API: `curl -X POST "http://localhost:8000/notify"`

---
*Для детальной информации см. полную техническую документацию*
