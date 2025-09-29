from pydantic import BaseModel, Field
from typing import Optional, Union
from datetime import datetime

class OrderData(BaseModel):
    """Данные заказа для уведомлений"""
    order_id: str = Field(..., description="ID заказа")
    vehicle_type: str = Field(..., description="Тип техники")
    location: str = Field(..., description="Локация")
    date_time: str = Field(..., description="Дата и время")
    price: str = Field(..., description="Стоимость")

class LaravelNotification(BaseModel):
    """Структура уведомления от Laravel"""
    telegram_id: Union[str, int] = Field(..., description="Telegram ID пользователя")
    order_data: OrderData = Field(..., description="Данные заказа")

class LegacyNotification(BaseModel):
    """Старая структура для обратной совместимости"""
    telegram_id: Union[str, int] = Field(..., description="Telegram ID пользователя")
    text: str = Field(..., description="Текст сообщения")
    url: Optional[str] = Field(None, description="URL для кнопки")

class TelegramRegistration(BaseModel):
    """Регистрация пользователя в Telegram"""
    phone: str = Field(..., pattern=r'^\+?\d{10,15}$', description="Номер телефона")
    telegram_id: Union[str, int] = Field(..., description="Telegram ID")

class ApiResponse(BaseModel):
    """Стандартный ответ API"""
    success: bool = Field(..., description="Статус операции")
    message: str = Field(..., description="Сообщение")
    data: Optional[dict] = Field(None, description="Дополнительные данные")
