from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from storage import add_user, remove_user
from config import BOT_TOKEN
import aiohttp

bot = Bot(token=BOT_TOKEN, parse_mode='Markdown')
dp = Dispatcher()

request_phone_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📱 Отправить номер", request_contact=True)]],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет! Пожалуйста, отправь свой номер телефона для регистрации.", reply_markup=request_phone_kb)

@dp.message(lambda m: m.contact)
async def phone_handler(message: types.Message):
    from config import LARAVEL_API_URL
    phone = message.contact.phone_number
    user_id = message.from_user.id

    async with aiohttp.ClientSession() as session:
        async with session.post(LARAVEL_API_URL, json={"phone": phone}) as resp:
            if resp.status == 200:
                add_user(user_id)
                await message.answer("✅ Вы успешно зарегистрированы!", reply_markup=ReplyKeyboardRemove())
            else:
                await message.answer("❌ Не удалось зарегистрироваться. Попробуйте позже.")

@dp.message(Command("stop"))
async def cmd_stop(message: types.Message):
    remove_user(message.from_user.id)
    await message.answer("Вы больше не будете получать уведомления.")
