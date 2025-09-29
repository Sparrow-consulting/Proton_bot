import asyncio
import aiohttp
import json
import pytest
from datetime import datetime

@pytest.mark.asyncio
async def test_bot_integration():
    """Тестирование интеграции бота"""
    
    # Конфигурация для тестов
    BOT_URL = "http://localhost:8000"
    API_TOKEN = "your-api-token-here"
    TEST_TELEGRAM_ID = "123456789"
    
    # Тестовые данные
    test_order_data = {
        "order_id": f"TEST-{int(datetime.now().timestamp())}",
        "vehicle_type": "Экскаватор",
        "location": "Москва, ул. Тестовая, 1",
        "date_time": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "price": "50 000 ₽"
    }
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("🤖 Тестирование интеграции Proton Telegram Bot")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Тест 1: Проверка здоровья
        print("\n🧪 Тест 1: Проверка здоровья бота...")
        try:
            async with session.get(f"{BOT_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Бот здоров: {data['data']['bot_username']}")
                    print(f"   Bot ID: {data['data']['bot_id']}")
                    print(f"   API URL: {data['data']['api_url']}")
                else:
                    print(f"❌ Бот недоступен: HTTP {response.status}")
                    return
        except Exception as e:
            print(f"❌ Ошибка подключения к боту: {e}")
            return
        
        # Тест 2: Проверка основного API
        print("\n🧪 Тест 2: Проверка основного API...")
        try:
            async with session.get(f"{BOT_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API доступен: {data['message']}")
                    print(f"   Доступные эндпоинты: {', '.join(data['data']['endpoints'])}")
                else:
                    print(f"❌ API недоступен: HTTP {response.status}")
        except Exception as e:
            print(f"❌ Ошибка API: {e}")
        
        # Тест 3: Отправка уведомления
        print("\n🧪 Тест 3: Отправка уведомления...")
        notification_data = {
            "telegram_id": TEST_TELEGRAM_ID,
            "order_data": test_order_data
        }
        
        try:
            async with session.post(
                f"{BOT_URL}/notify",
                json=notification_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Уведомление отправлено: {data['message']}")
                    print(f"   Telegram ID: {data['data']['telegram_id']}")
                    print(f"   Order ID: {data['data']['order_id']}")
                elif response.status == 401:
                    print("⚠️  Ошибка аутентификации - проверьте LARAVEL_BEARER_TOKEN")
                else:
                    print(f"❌ Ошибка отправки: HTTP {response.status}")
                    error_data = await response.text()
                    print(f"   Детали: {error_data}")
        except Exception as e:
            print(f"❌ Исключение при отправке уведомления: {e}")
        
        # Тест 4: Legacy уведомление
        print("\n🧪 Тест 4: Legacy уведомление...")
        legacy_data = {
            "telegram_id": TEST_TELEGRAM_ID,
            "text": "🚛 Тестовое уведомление от старого API",
            "url": "https://app.protonrent.ru/orders/test"
        }
        
        legacy_headers = {
            "X-API-Key": "proton-telegram-secret-2024",
            "Content-Type": "application/json"
        }
        
        try:
            async with session.post(
                f"{BOT_URL}/notify-legacy",
                json=legacy_data,
                headers=legacy_headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Legacy уведомление отправлено: {data['message']}")
                elif response.status == 401:
                    print("⚠️  Ошибка аутентификации legacy API - проверьте X-API-Key")
                else:
                    print(f"❌ Ошибка legacy уведомления: HTTP {response.status}")
                    error_data = await response.text()
                    print(f"   Детали: {error_data}")
        except Exception as e:
            print(f"❌ Исключение при отправке legacy уведомления: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Тестирование завершено!")
    print("\n📋 Рекомендации:")
    print("1. Убедитесь, что бот запущен: python -m uvicorn main:app --host 0.0.0.0 --port 8000")
    print("2. Проверьте токены в .env файле")
    print("3. Для реального тестирования используйте настоящий Telegram ID")
    print("4. Проверьте логи бота в файле bot.log")

if __name__ == "__main__":
    asyncio.run(test_bot_integration())
