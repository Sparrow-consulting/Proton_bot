
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле")

# Laravel API
API_URL = os.getenv("API_URL", "https://app.protonrent.ru/api/v1")
LARAVEL_BEARER_TOKEN = os.getenv("LARAVEL_BEARER_TOKEN")
NOTIFY_SECRET = os.getenv("NOTIFY_SECRET")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

# Bot settings
BOT_HOST = os.getenv("BOT_HOST", "0.0.0.0")
BOT_PORT = int(os.getenv("BOT_PORT", 8000))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "bot.log")

# Validation
if not NOTIFY_SECRET:
    raise ValueError("NOTIFY_SECRET не найден в .env файле")
