# 🤖 Proton Telegram Bot v2.0

Telegram бот для платформы аренды спецтехники Proton с полной интеграцией с Laravel backend.

## 🚀 Быстрый старт

### 1. Настройка окружения

```bash
# Копируем пример конфигурации
cp .env.example .env

# Редактируем .env файл
nano .env
```

Обязательные переменные:
```env
BOT_TOKEN=your-telegram-bot-token
API_URL=https://app.protonrent.ru/api/v1
NOTIFY_SECRET=proton-telegram-secret-2024
LARAVEL_BEARER_TOKEN=your-laravel-api-token
```

### 2. Установка зависимостей

```bash
# Создание виртуального окружения
python -m venv .venv

# Активация окружения
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### 3. Запуск бота

```bash
# Простой запуск
chmod +x start_bot.sh
./start_bot.sh

# Или вручную
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📋 API Endpoints

### 🏠 Основные эндпоинты

#### `GET /`
Информация о боте и доступных эндпоинтах

#### `GET /health`
Проверка здоровья сервиса
- Возвращает информацию о боте и статусе подключения

### 📨 Уведомления

#### `POST /notify`
**Основной эндпоинт для уведомлений от Laravel**

**Аутентификация:** Bearer token
```bash
Authorization: Bearer your-laravel-api-token
```

**Структура запроса:**
```json
{
  "telegram_id": "123456789",
  "order_data": {
    "order_id": "ORDER-123",
    "vehicle_type": "Экскаватор",
    "location": "Москва, ул. Примерная, 1",
    "date_time": "15.01.2024 14:30",
    "price": "50 000 ₽"
  }
}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Notification sent successfully",
  "data": {
    "telegram_id": "123456789",
    "order_id": "ORDER-123"
  }
}
```

#### `POST /notify-legacy`
**Эндпоинт для обратной совместимости**

**Аутентификация:** X-API-Key
```bash
X-API-Key: proton-telegram-secret-2024
```

**Структура запроса:**
```json
{
  "telegram_id": "123456789",
  "text": "🚛 Новая заявка на аренду спецтехники",
  "url": "https://app.protonrent.ru/orders/123"
}
```

## 🤖 Команды бота

### `/start`
Регистрация пользователя в системе
- Запрашивает номер телефона
- Связывает Telegram ID с аккаунтом в Laravel

### `/stop`
Отписка от уведомлений
- Отключает уведомления для пользователя
- Вызывает Laravel API для обновления статуса

### `/id`
Показать Telegram ID пользователя
- Полезно для отладки и настройки

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `BOT_TOKEN` | Токен Telegram бота | - |
| `API_URL` | URL Laravel API | `https://app.protonrent.ru/api/v1` |
| `LARAVEL_BEARER_TOKEN` | Bearer token для Laravel | - |
| `NOTIFY_SECRET` | Секрет для legacy API | - |
| `WEBHOOK_SECRET` | Секрет для webhook | - |
| `BOT_HOST` | Хост для запуска | `0.0.0.0` |
| `BOT_PORT` | Порт для запуска | `8000` |
| `DEBUG` | Режим отладки | `false` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |
| `LOG_FILE` | Файл для логов | `bot.log` |

### Laravel конфигурация

В `.env` файле Laravel добавьте:
```env
TELEGRAM_BOT_API_URL=http://localhost:8000
TELEGRAM_BOT_API_TOKEN=your-api-token-here
TELEGRAM_NOTIFY_SECRET=proton-telegram-secret-2024
```

## 🧪 Тестирование

### Автоматическое тестирование
```bash
python test_integration.py
```

### Ручное тестирование API

#### Проверка здоровья
```bash
curl http://localhost:8000/health
```

#### Отправка уведомления
```bash
curl -X POST http://localhost:8000/notify \
  -H "Authorization: Bearer your-api-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": "123456789",
    "order_data": {
      "order_id": "TEST-123",
      "vehicle_type": "Экскаватор",
      "location": "Москва",
      "date_time": "15.01.2024 14:30",
      "price": "50 000 ₽"
    }
  }'
```

#### Legacy уведомление
```bash
curl -X POST http://localhost:8000/notify-legacy \
  -H "X-API-Key: proton-telegram-secret-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": "123456789",
    "text": "Тестовое сообщение",
    "url": "https://example.com"
  }'
```

## 🔍 Мониторинг и логирование

### Логи
- **Файл логов:** `bot.log`
- **Консольные логи:** включены по умолчанию
- **Уровни:** DEBUG, INFO, WARNING, ERROR

### Мониторинг
- **Health check:** `GET /health`
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 🚨 Устранение неполадок

### Бот не запускается
1. Проверьте `.env` файл
2. Убедитесь, что все зависимости установлены
3. Проверьте токен бота в @BotFather

### API не отвечает
1. Проверьте, что бот запущен на правильном порту
2. Убедитесь, что токены аутентификации корректны
3. Проверьте логи в `bot.log`

### Уведомления не доходят
1. Проверьте Telegram ID пользователя
2. Убедитесь, что пользователь не заблокировал бота
3. Проверьте логи отправки сообщений

### Ошибки аутентификации
1. Проверьте Bearer token в Laravel
2. Убедитесь, что X-API-Key совпадает в обеих системах
3. Проверьте headers запросов

## 🔄 Интеграция с Laravel

### Использование TelegramBotIntegrationService

```php
use App\Services\TelegramBotIntegrationService;

// Отправка уведомления
$telegramService = new TelegramBotIntegrationService();
$success = $telegramService->sendNotification($telegramId, [
    'order_id' => $order->id,
    'vehicle_type' => $order->vehicleType->name,
    'location' => $order->getLocation(),
    'date_time' => $order->created_at->format('d.m.Y H:i'),
    'price' => number_format($order->total_price, 0, ',', ' ') . ' ₽'
]);

// Проверка здоровья бота
$health = $telegramService->checkBotHealth();
```

### Обновление существующих уведомлений

В `SendTelegramNotificationJob.php`:
```php
public function handle(TelegramBotIntegrationService $telegramService): void
{
    $orderData = [
        'order_id' => $this->order->id,
        'vehicle_type' => $this->order->vehicleType->name ?? 'Не указан',
        'location' => $this->getOrderLocation(),
        'date_time' => $this->order->created_at->format('d.m.Y H:i'),
        'price' => number_format($this->order->total_price ?? 0, 0, ',', ' ') . ' ₽'
    ];

    $telegramService->sendNotification($this->user->telegram_id, $orderData);
}
```

## 🏗️ Архитектура

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Laravel App   │    │  Telegram Bot    │    │  Telegram API   │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │                 │
│ │TelegramBot  │◄├────┤►│ FastAPI      │ │    │                 │
│ │Integration  │ │HTTP│ │ /notify      │ │    │                 │
│ │Service      │ │    │ │ /health      │ │    │                 │
│ └─────────────┘ │    │ └──────────────┘ │    │                 │
│                 │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ ┌─────────────┐ │    │ │ Aiogram      │◄├────┤►│ Bot API     │ │
│ │Notification │ │    │ │ Handlers     │ │    │ │ Webhook     │ │
│ │Jobs         │ │    │ │ /start /stop │ │    │ └─────────────┘ │
│ └─────────────┘ │    │ └──────────────┘ │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📞 Поддержка

### Контакты
- **Команда разработки:** Proton Development Team
- **Документация:** [TELEGRAM_INTEGRATION.md](../ProtonBackend-GitLab/TELEGRAM_INTEGRATION.md)
- **Техническое задание:** [TELEGRAM_BOT_FIX_SPECIFICATION.md](../ProtonBackend-GitLab/TELEGRAM_BOT_FIX_SPECIFICATION.md)

### Версии
- **Текущая версия:** 2.0.0
- **Совместимость:** Laravel 10+, Python 3.8+, aiogram 3.4+

---

**🎯 Статус:** ✅ Готов к production использованию  
**📅 Обновлено:** Сентябрь 2025  
**🔄 Следующее обновление:** По мере необходимости