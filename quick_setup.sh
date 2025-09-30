#!/bin/bash

# ================================================
# PROTON BOT - БЫСТРАЯ НАСТРОЙКА
# ================================================

echo "🚀 Быстрая настройка Proton Telegram Bot..."
echo ""

# Проверка что мы в правильной директории
if [ ! -f "main.py" ]; then
    echo "❌ Ошибка: запустите скрипт из директории Proton_bot"
    exit 1
fi

# Создание .env файла
echo "📝 Создаю .env файл..."
cat > .env << 'EOF'
# Telegram Bot
BOT_TOKEN=7923122647:AAEHvu3KMz2J-9L-nmKH0jKf1TyWGdcdZ7c

# Laravel API
API_URL=https://app.protonrent.ru/api/v1

# Bearer токен
LARAVEL_BEARER_TOKEN=68e21a0a7ce5193998a8289301a59b6e

# Security
NOTIFY_SECRET=proton-telegram-secret-2024
WEBHOOK_SECRET=proton-secret-webhook-2024

# Server
BOT_HOST=0.0.0.0
BOT_PORT=8000
DEBUG=false

# Logging
LOG_LEVEL=INFO
LOG_FILE=bot.log
EOF

echo "✅ .env файл создан!"
echo ""

# Проверка виртуального окружения
if [ ! -d ".venv" ]; then
    echo "📦 Создаю виртуальное окружение..."
    python3 -m venv .venv
    echo "✅ Виртуальное окружение создано!"
    echo ""
fi

# Активация и установка зависимостей
echo "📥 Устанавливаю зависимости..."
source .venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Зависимости установлены!"
echo ""

echo "✨ НАСТРОЙКА ЗАВЕРШЕНА!"
echo ""
echo "🎯 Следующие шаги:"
echo "1. Если нужно, отредактируйте .env файл"
echo "2. Запустите бота:"
echo "   ./start_bot.sh"
echo "   или"
echo "   python -m uvicorn main:app --host 0.0.0.0 --port 8000"
echo ""
echo "📊 Проверка здоровья:"
echo "   curl http://localhost:8000/health"
echo ""
