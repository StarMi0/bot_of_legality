from aiogram import Router, Bot, types
from aiogram.filters import StateFilter
from aiogram.types import Message

from database.request import for_chat_id

router = Router(name=__name__)

"""
ВЕТКА ПЕРЕПИСОК
"""

@router.message(StateFilter(None))
async def handle_message(message: Message, bot: Bot):
    user_id = str(message.from_user.id)
    chat_info = await for_chat_id(user_id)

    if not chat_info:
        await message.answer("У вас нет активных заказов")
        return

    to_id = chat_info["to_id"]
    if not to_id:
        await message.answer("Не выбран исполнитель по заказу")
        return

    # Пересылаем сообщение
    if message.text:
        await bot.send_message(chat_id=to_id, text=message.text)
    elif message.photo:
        await bot.send_photo(chat_id=to_id, photo=message.photo[-1].file_id, caption=message.caption)
    elif message.document:
        await bot.send_document(chat_id=to_id, document=message.document.file_id, caption=message.caption)
    else:
        await message.answer("Неподдерживаемый тип сообщения")