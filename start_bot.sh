#!/bin/bash

echo "🤖 Запуск Proton Telegram Bot v2.0"
echo "=================================="

# Проверка .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "📋 Создайте файл .env на основе следующего шаблона:"
    echo ""
    echo "BOT_TOKEN=your-bot-token-here"
    echo "API_URL=https://app.protonrent.ru/api/v1"
    echo "NOTIFY_SECRET=proton-telegram-secret-2024"
    echo "LARAVEL_BEARER_TOKEN=your-api-token-here"
    echo "WEBHOOK_SECRET=telegram-webhook-secret-2024"
    echo "BOT_HOST=0.0.0.0"
    echo "BOT_PORT=8000"
    echo "DEBUG=false"
    echo "LOG_LEVEL=INFO"
    echo "LOG_FILE=bot.log"
    echo ""
    exit 1
fi

# Проверка Python окружения
if [ ! -d ".venv" ]; then
    echo "🐍 Создание виртуального окружения..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ Не удалось создать виртуальное окружение"
        echo "Убедитесь, что Python 3.8+ установлен"
        exit 1
    fi
fi

# Активация окружения
echo "🔄 Активация виртуального окружения..."
source .venv/bin/activate

# Проверка pip
pip --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ pip не найден в виртуальном окружении"
    exit 1
fi

# Установка зависимостей
echo "📦 Установка зависимостей..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Ошибка установки зависимостей"
    exit 1
fi

# Проверка основных модулей
echo "🔍 Проверка модулей..."
python -c "import fastapi, aiogram, aiohttp, pydantic" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Не все модули установлены корректно"
    exit 1
fi

# Проверка конфигурации
echo "⚙️  Проверка конфигурации..."
python -c "from config import BOT_TOKEN, API_URL; print('✅ Конфигурация загружена')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Ошибка в файле конфигурации"
    echo "Проверьте файлы .env и config.py"
    exit 1
fi

# Создание лог файла если не существует
touch bot.log

echo "🚀 Запуск Telegram бота..."
echo "📍 URL: http://localhost:8000"
echo "📋 Документация: http://localhost:8000/docs"
echo "💚 Здоровье: http://localhost:8000/health"
echo ""
echo "Для остановки нажмите Ctrl+C"
echo ""

# Запуск бота
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
