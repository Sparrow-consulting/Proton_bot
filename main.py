import os
import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from fastapi import FastAPI, Header
from pydantic import BaseModel
from dotenv import load_dotenv
import re

# Загрузка .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")
NOTIFY_SECRET = os.getenv("NOTIFY_SECRET")

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# FastAPI-приложение
app = FastAPI()


# --- Telegram-хендлеры ---

@dp.message(Command("start"))
async def handle_start(message: Message):
    button = KeyboardButton(text="📞 Поделиться контактом", request_contact=True)
    kb = ReplyKeyboardMarkup(
        keyboard=[[button]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Пожалуйста, подтвердите номер телефона:", reply_markup=kb)


@dp.message(Command("stop"))
async def handle_stop(message: Message):
    telegram_id = message.from_user.id
    try:
        response = requests.post(
            f"{API_URL}/telegram/unsubscribe",
            json={"telegram_id": telegram_id}
        )
        if response.status_code == 200:
            await message.answer("Вы успешно отписались от уведомлений.")
        else:
            logging.warning(f"Ошибка отписки: {response.status_code} {response.text}")
            await message.answer("Ошибка при отписке. Повторите позже.")
    except Exception as e:
        logging.error(f"Ошибка отписки: {e}")
        await message.answer("Сервис временно недоступен.")


@dp.message(Command("id"))
async def handle_id(message: Message):
    telegram_id = message.from_user.id
    await message.answer(f"Ваш Telegram ID: {telegram_id}")


@dp.message(lambda msg: msg.contact is not None)
async def handle_contact(message: Message):
    contact = message.contact
    telegram_id = message.from_user.id
    phone_number = contact.phone_number

    # 💡 Проверка формата номера
    if not re.match(r"^\+?\d{10,15}$", phone_number):
        await message.answer("Похоже, номер телефона передан в неверном формате.")
        return

    try:
        response = requests.post(
            f"{API_URL}/telegram/register",
            json={"phone": phone_number, "telegram_id": telegram_id}
        )
        if response.status_code == 200:
            logging.info(f"Зарегистрирован telegram_id={telegram_id} для phone={phone_number}")
            await message.answer("✅ Регистрация прошла успешно! Теперь вы будете получать уведомления.")
        else:
            logging.warning(f"Ошибка регистрации: {response.status_code} {response.text}")
            await message.answer("⚠️ Что-то пошло не так. Попробуйте позже.")
    except Exception as e:
        logging.error(f"Ошибка при регистрации: {e}")
        await message.answer("Сервис временно недоступен.")


# --- FastAPI endpoint для Laravel ---

class Notification(BaseModel):
    telegram_id: int
    text: str
    url: str | None = None


@app.post("/notify")
async def notify(data: Notification, x_api_key: str = Header(default=None)):
    if NOTIFY_SECRET and x_api_key != NOTIFY_SECRET:
        logging.warning("Запрос отклонён: неверный API ключ")
        return {"status": "error", "detail": "Invalid API key"}

    message_text = data.text
    reply_markup = None

    if data.url:
        message_text += f"\n\n🔗 <a href=\"{data.url}\">Перейти к заявке</a>"
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Перейти к заявке", url=data.url)]]
        )

    try:
        await bot.send_message(chat_id=data.telegram_id, text=message_text, reply_markup=reply_markup, parse_mode="HTML")
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"Ошибка при отправке уведомления: {e}")
        return {"status": "error", "detail": str(e)}


# --- Startup ---

@app.on_event("startup")
async def on_startup():
    logging.info("📡 Telegram-бот запущен")

    commands = [
        BotCommand(command="start", description="Регистрация и запуск бота"),
        BotCommand(command="id", description="Показать ваш Telegram ID"),
        BotCommand(command="stop", description="Отписаться от уведомлений")
    ]
    await bot.set_my_commands(commands)

    asyncio.create_task(dp.start_polling(bot))
