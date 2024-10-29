from aiogram.filters import BaseFilter
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message

from utils.states import Consult

"""Хэндмэйд фильтр для проверки на админа"""


class DialogFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        from main import bot, dp
        user_id = int(message.from_user.id)
        user_state = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
        if await dp.storage.get_state(key=user_state) == Consult.lawyer_client_chat:
            return True
        else:
            return False
