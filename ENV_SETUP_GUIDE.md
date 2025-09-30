# 🔧 Proton Telegram Bot - Environment Setup Guide

## Конфигурация переменных окружения

Создайте файл `.env` в корне проекта со следующим содержимым:

```env
# ================================================
# PROTON TELEGRAM BOT - CONFIGURATION
# ================================================

# ------------------------------------------------
# Telegram Bot Settings
# ------------------------------------------------

# Токен Telegram бота (получить у @BotFather)
BOT_TOKEN=your-bot-token-here

# ------------------------------------------------
# Laravel Backend Integration
# ------------------------------------------------

# URL Laravel API для регистрации пользователей и управления уведомлениями
API_URL=https://app.protonrent.ru/api/v1

# Bearer токен для аутентификации запросов к Laravel API
# Должен совпадать с TELEGRAM_BOT_API_TOKEN в Backend .env
# Сгенерировать: php artisan chatbot:generate-token (в ProtonBackend)
LARAVEL_BEARER_TOKEN=your-laravel-api-token-here

# ------------------------------------------------
# Security
# ------------------------------------------------

# Секрет для legacy API эндпоинта /notify-legacy (X-API-Key)
NOTIFY_SECRET=proton-telegram-secret-2024

# Секрет для webhook от Telegram (X-Telegram-Bot-Api-Secret-Token)
WEBHOOK_SECRET=your-webhook-secret-token

# ------------------------------------------------
# Bot Server Settings
# ------------------------------------------------

# Хост для запуска FastAPI сервера
BOT_HOST=0.0.0.0

# Порт для запуска FastAPI сервера
BOT_PORT=8000

# Режим отладки (true/false)
DEBUG=false

# ------------------------------------------------
# Logging Settings
# ------------------------------------------------

# Уровень логирования: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Файл для логов
LOG_FILE=bot.log
```

## 📋 Соответствие переменных с ProtonBackend

| Proton_bot | ProtonBackend | Описание |
|------------|---------------|----------|
| `BOT_TOKEN` | `TELEGRAM_BOT_TOKEN` | Токен от @BotFather |
| `API_URL` | `APP_URL` + `/api/v1` | URL Laravel API |
| `LARAVEL_BEARER_TOKEN` | `TELEGRAM_BOT_API_TOKEN` | **Должны совпадать!** |
| `NOTIFY_SECRET` | - | Для legacy API |
| `WEBHOOK_SECRET` | `TELEGRAM_SECRET_TOKEN` | Для проверки webhook |
| Port `8000` | `TELEGRAM_BOT_API_URL` | URL бота в Backend |

## 🚀 Быстрая настройка

### 1. Создайте .env файл

```bash
cd /Users/vorobevavd/PROTON_BOT_2_2/Proton_bot
touch .env
nano .env  # или используйте любой редактор
```

### 2. Минимальная конфигурация для запуска

```env
BOT_TOKEN=7923122647:AAEHvu3KMz2J-9L-nmKH0jKf1TyWGdcdZ7c
API_URL=https://app.protonrent.ru/api/v1
LARAVEL_BEARER_TOKEN=ПОЛУЧИТЬ_ИЗ_BACKEND
NOTIFY_SECRET=proton-telegram-secret-2024
BOT_HOST=0.0.0.0
BOT_PORT=8000
DEBUG=false
LOG_LEVEL=INFO
LOG_FILE=bot.log
```

### 3. Получите Bearer токен из Backend

```bash
cd /Users/vorobevavd/ProtonBackend/ProtonBackend-GitLab
php artisan chatbot:generate-token --user-id=1
```

Команда выведет:
```
ChatBot API Token generated successfully!
Token: abc123def456ghi789

Add to your .env files:
Backend: TELEGRAM_BOT_API_TOKEN=abc123def456ghi789
ChatBot: LARAVEL_BEARER_TOKEN=abc123def456ghi789
```

### 4. Обновите оба .env файла

**ProtonBackend (.env):**
```env
TELEGRAM_BOT_API_TOKEN=abc123def456ghi789
```

**Proton_bot (.env):**
```env
LARAVEL_BEARER_TOKEN=abc123def456ghi789
```

## ✅ Проверка конфигурации

```bash
# Проверить что все переменные загружены
python -c "from config import *; print(f'''
BOT_TOKEN: {BOT_TOKEN[:10]}...
API_URL: {API_URL}
LARAVEL_BEARER_TOKEN: {LARAVEL_BEARER_TOKEN[:10] if LARAVEL_BEARER_TOKEN else "NOT SET"}...
BOT_HOST: {BOT_HOST}
BOT_PORT: {BOT_PORT}
''')"
```

## 🔍 Типичные ошибки

### ❌ "BOT_TOKEN не найден в .env файле"
**Решение**: Убедитесь что файл `.env` существует и содержит `BOT_TOKEN=...`

### ❌ "NOTIFY_SECRET не найден в .env файле"
**Решение**: Добавьте `NOTIFY_SECRET=proton-telegram-secret-2024` в `.env`

### ❌ "Invalid authentication token" при вызове /notify
**Решение**: Проверьте что `LARAVEL_BEARER_TOKEN` совпадает с `TELEGRAM_BOT_API_TOKEN` в Backend

## 📝 Пример полного .env для production

```env
# Telegram Bot
BOT_TOKEN=7923122647:AAEHvu3KMz2J-9L-nmKH0jKf1TyWGdcdZ7c

# Laravel API
API_URL=https://app.protonrent.ru/api/v1
LARAVEL_BEARER_TOKEN=abc123def456ghi789

# Security
NOTIFY_SECRET=proton-telegram-secret-2024
WEBHOOK_SECRET=my-webhook-secret-2024

# Server
BOT_HOST=0.0.0.0
BOT_PORT=8000
DEBUG=false

# Logging
LOG_LEVEL=INFO
LOG_FILE=bot.log
```

## 📝 Пример .env для local development

```env
# Telegram Bot
BOT_TOKEN=7923122647:AAEHvu3KMz2J-9L-nmKH0jKf1TyWGdcdZ7c

# Laravel API (local)
API_URL=http://localhost:8001/api/v1
LARAVEL_BEARER_TOKEN=test-token-for-local-dev

# Security
NOTIFY_SECRET=test-secret
WEBHOOK_SECRET=test-webhook-secret

# Server
BOT_HOST=127.0.0.1
BOT_PORT=8000
DEBUG=true

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=bot.log
```
