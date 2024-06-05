from aiogram.filters import BaseFilter
from aiogram.types import Message
from utils.admin_checking import admin_check

"""Хэндмэйд фильтр для проверки на админа"""
class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if await admin_check(message.from_user.id):
            return True
        else:
            return False