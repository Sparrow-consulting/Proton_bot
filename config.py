
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

# eBot API (for compatibility with GitLab CI/CD script)
EBOT_API_TOKEN = os.getenv("EBOT_API_TOKEN") or LARAVEL_BEARER_TOKEN
EBOT_HMAC_SECRET = os.getenv("EBOT_HMAC_SECRET") or WEBHOOK_SECRET

# Bot settings
BOT_HOST = os.getenv("BOT_HOST", "0.0.0.0")
BOT_PORT = int(os.getenv("BOT_PORT", 8000))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "bot.log")

# Validation
if not NOTIFY_SECRET:
    raise ValueError("NOTIFY_SECRET не найден в .env файле")

# Ensure eBot secrets are available
if not EBOT_API_TOKEN:
    raise ValueError("EBOT_API_TOKEN или LARAVEL_BEARER_TOKEN не найден в .env файле")
if not EBOT_HMAC_SECRET:
    raise ValueError("EBOT_HMAC_SECRET или WEBHOOK_SECRET не найден в .env файле")
