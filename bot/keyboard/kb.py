from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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