# Proton_bot
FastAPI-эндпоинт `/notify` + Telegram-бот (aiogram).

## Локальный запуск
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

## Пример ENV
см. `.env.example` (реальные значения не коммитим).
