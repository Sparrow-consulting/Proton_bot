import os
import logging
import asyncio
import aiohttp
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from contextlib import asynccontextmanager
from typing import Union

from models import LaravelNotification, LegacyNotification, TelegramRegistration, ApiResponse, OrderData
from config import *
from storage import init_db

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Security
security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Проверка Bearer token"""
    if credentials.credentials != LARAVEL_BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return credentials.credentials

async def verify_legacy_api_key(x_api_key: str = Header(default=None)):
    """Проверка X-API-Key для обратной совместимости"""
    if x_api_key != NOTIFY_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    logger.info("🚀 Запуск Telegram бота...")
    
    # Инициализируем базу данных
    init_db()
    logger.info("✅ База данных инициализирована")
    
    # Устанавливаем команды бота
    commands = [
        BotCommand(command="start", description="Регистрация и запуск бота"),
        BotCommand(command="id", description="Показать ваш Telegram ID"),
        BotCommand(command="stop", description="Отписаться от уведомлений")
    ]
    await bot.set_my_commands(commands)
    
    # Запускаем polling в фоне
    asyncio.create_task(dp.start_polling(bot))
    logger.info("✅ Telegram бот запущен успешно")
    
    yield
    
    # Shutdown
    logger.info("🛑 Остановка Telegram бота...")
    await bot.session.close()

app = FastAPI(
    title="Proton Telegram Bot API",
    description="API для интеграции Telegram бота с Laravel backend",
    version="2.0.0",
    lifespan=lifespan
)

# --- Telegram обработчики ---

@dp.message(Command("start"))
async def handle_start(message: Message):
    """Обработка команды /start"""
    button = KeyboardButton(text="📞 Поделиться контактом", request_contact=True)
    kb = ReplyKeyboardMarkup(
        keyboard=[[button]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    welcome_text = (
        "👋 <b>Добро пожаловать в Proton!</b>\n\n"
        "Для получения уведомлений о новых заявках на аренду спецтехники, "
        "пожалуйста, поделитесь своим номером телефона."
    )
    
    await message.answer(welcome_text, reply_markup=kb, parse_mode="HTML")
    logger.info(f"Пользователь {message.from_user.id} начал регистрацию")

@dp.message(Command("stop"))
async def handle_stop(message: Message):
    """Обработка команды /stop"""
    telegram_id = str(message.from_user.id)
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {LARAVEL_BEARER_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            async with session.post(
                f"{API_URL}/telegram/disable-notifications",
                json={"telegram_id": telegram_id},
                headers=headers
            ) as response:
                if response.status == 200:
                    # Удаляем пользователя из локальной БД
                    from storage import remove_user
                    remove_user(int(telegram_id))
                    
                    await message.answer("🔕 Вы успешно отписались от уведомлений.")
                    logger.info(f"Пользователь {telegram_id} отписался от уведомлений")
                else:
                    logger.warning(f"Ошибка отписки пользователя {telegram_id}: {response.status}")
                    await message.answer("⚠️ Произошла ошибка при отписке. Попробуйте позже.")
                    
    except Exception as e:
        logger.error(f"Ошибка при отписке пользователя {telegram_id}: {e}")
        await message.answer("❌ Сервис временно недоступен. Попробуйте позже.")

@dp.message(Command("id"))
async def handle_id(message: Message):
    """Показать Telegram ID пользователя"""
    telegram_id = message.from_user.id
    await message.answer(f"🆔 Ваш Telegram ID: <code>{telegram_id}</code>", parse_mode="HTML")

@dp.message(lambda msg: msg.contact is not None)
async def handle_contact(message: Message):
    """Обработка контакта пользователя"""
    contact = message.contact
    telegram_id = str(message.from_user.id)
    phone_number = contact.phone_number
    
    # Нормализация номера телефона
    phone_number = phone_number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number
    
    logger.info(f"Получен контакт от пользователя {telegram_id}: {phone_number}")
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {LARAVEL_BEARER_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            registration_data = {
                "phone": phone_number,
                "telegram_id": telegram_id
            }
            
            async with session.post(
                f"{API_URL}/telegram/register",
                json=registration_data,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    # Добавляем пользователя в локальную БД для уведомлений
                    from storage import add_user
                    add_user(int(telegram_id))
                    
                    success_text = (
                        "✅ <b>Регистрация успешна!</b>\n\n"
                        "Теперь вы будете получать уведомления о новых заявках "
                        "на аренду спецтехники, соответствующих вашему оборудованию."
                    )
                    await message.answer(success_text, parse_mode="HTML")
                    logger.info(f"Пользователь {telegram_id} успешно зарегистрирован с номером {phone_number}")
                    
                elif response.status == 404:
                    error_text = (
                        "❌ <b>Пользователь не найден</b>\n\n"
                        "Ваш номер телефона не зарегистрирован в системе Proton. "
                        "Пожалуйста, сначала зарегистрируйтесь в приложении или на сайте."
                    )
                    await message.answer(error_text, parse_mode="HTML")
                    logger.warning(f"Пользователь с номером {phone_number} не найден в системе")
                    
                else:
                    logger.error(f"Ошибка регистрации пользователя {telegram_id}: HTTP {response.status}")
                    await message.answer("⚠️ Произошла ошибка при регистрации. Попробуйте позже.")
                    
    except Exception as e:
        logger.error(f"Исключение при регистрации пользователя {telegram_id}: {e}")
        await message.answer("❌ Сервис временно недоступен. Попробуйте позже.")

# --- FastAPI эндпоинты ---

@app.get("/", response_model=ApiResponse)
async def root():
    """Информация о боте"""
    return ApiResponse(
        success=True,
        message="Proton Telegram Bot API v2.0.0",
        data={
            "status": "active",
            "endpoints": ["/notify", "/notify-legacy", "/health"],
            "telegram_bot": "@proton_rent_bot"
        }
    )

@app.get("/health", response_model=ApiResponse)
async def health_check():
    """Проверка здоровья сервиса"""
    try:
        bot_info = await bot.get_me()
        return ApiResponse(
            success=True,
            message="Service is healthy",
            data={
                "bot_username": bot_info.username,
                "bot_id": bot_info.id,
                "api_url": API_URL
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/notify", response_model=ApiResponse)
async def notify_laravel(
    data: LaravelNotification,
    token: str = Depends(verify_api_key)
):
    """
    Основной эндпоинт для уведомлений от Laravel
    Использует новую структуру данных с Bearer token аутентификацией
    """
    telegram_id = str(data.telegram_id)
    order_data = data.order_data
    
    logger.info(f"Получено уведомление от Laravel для пользователя {telegram_id}, заказ {order_data.order_id}")
    
    # Формируем красивое сообщение
    message_text = (
        "🚛 <b>Новая заявка на аренду спецтехники</b>\n\n"
        f"📋 <b>Тип техники:</b> {order_data.vehicle_type}\n"
        f"📍 <b>Локация:</b> {order_data.location}\n"
        f"📅 <b>Дата и время:</b> {order_data.date_time}\n"
        f"💰 <b>Стоимость:</b> {order_data.price}\n\n"
        "Нажмите кнопку ниже для просмотра деталей заявки."
    )
    
    # Создаем inline кнопку
    # Используем order_url если передан, иначе формируем из order_id
    order_url = order_data.order_url or f"https://app.protonrent.ru/orders/{order_data.order_id}"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="📋 Перейти к заявке",
                url=order_url
            )
        ]]
    )
    
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        logger.info(f"Уведомление успешно отправлено пользователю {telegram_id}")
        return ApiResponse(
            success=True,
            message="Notification sent successfully",
            data={"telegram_id": telegram_id, "order_id": order_data.order_id}
        )
        
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления пользователю {telegram_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send notification: {str(e)}"
        )

@app.post("/notify-legacy", response_model=ApiResponse)
async def notify_legacy(
    data: LegacyNotification,
    api_key: str = Depends(verify_legacy_api_key)
):
    """
    Эндпоинт для обратной совместимости со старой структурой данных
    Использует X-API-Key аутентификацию
    """
    telegram_id = str(data.telegram_id)
    
    logger.info(f"Получено legacy уведомление для пользователя {telegram_id}")
    
    # Подготавливаем клавиатуру если есть URL
    reply_markup = None
    if data.url:
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="🔗 Перейти", url=data.url)
            ]]
        )
    
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=data.text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        
        logger.info(f"Legacy уведомление успешно отправлено пользователю {telegram_id}")
        return ApiResponse(
            success=True,
            message="Legacy notification sent successfully",
            data={"telegram_id": telegram_id}
        )
        
    except Exception as e:
        logger.error(f"Ошибка отправки legacy уведомления пользователю {telegram_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send legacy notification: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=BOT_HOST,
        port=BOT_PORT,
        reload=DEBUG,
        log_level=LOG_LEVEL.lower()
    )