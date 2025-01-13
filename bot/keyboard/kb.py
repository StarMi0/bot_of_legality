from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.request import get_active_order, get_order_info_by_order_id
from utils.callbackdata import BranchChoose


user_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Поддержка")],
        [KeyboardButton(text="Создать заказ")],
        [KeyboardButton(text="Мои заказы")],
        [KeyboardButton(text="Диалог")],
    ],
    resize_keyboard=True
)


lawyer_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Поддержка")],
        [KeyboardButton(text="Мои заказы")],
        [KeyboardButton(text="Диалог")],
    ],
    resize_keyboard=True
)