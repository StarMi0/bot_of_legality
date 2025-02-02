from aiogram import Router, Bot, F
from aiogram.filters import BaseFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from database.request import get_lawyers, end_order, get_admins, get_active_order_by_lawyer, get_order_info_by_order_id
from keyboard.kb import lawyer_keyboard
from routers.states import EndOrder

router = Router(name=__name__)


# Кастомный фильтр для проверки пользователей
class LawyerFilter(BaseFilter):
    """Фильтр для проверки, является ли пользователь зарегистрированным как пользователь."""

    async def __call__(self, message: Message) -> bool:
        LAWYERS_DB = await get_lawyers()  # Временный список пользователей
        return str(message.from_user.id) in LAWYERS_DB

"""
ОСНОВНОЙ ФУНКЦИОНАЛ
"""

@router.message(Command("start"), LawyerFilter())
async def get_start(message: Message, bot: Bot):
    """
    Main start handler
    :param message:
    :param bot:
    :return:
    """
    # Текст инструкции
    instruction = (
        "Добро пожаловать в нашего бота!\n\n"
        "Здесь вы можете:\n"
        "1. Обратиться в поддержку.\n"
        "3. Просмотреть свои заказы.\n\n"
        "Выберите нужный пункт меню ниже."
    )

    # Отправляем сообщение с инструкцией и клавиатурой
    await message.answer(instruction, reply_markup=lawyer_keyboard)

