from aiogram import types
from aiogram.utils.media_group import MediaGroupBuilder

# from database.request import get
from loguru import logger


"""Файл содержит функции для рассылки сообщений"""


# async def broadcast(text) -> int:
#     """
#     Safe messages sender
#     Обработчик ошибок при рассылке
#     """
#     all_users = await get_all_users_ids() #  [645487713, 739424080]  #
#     counter = 0
#     for chat_id in all_users:
#         counter += await send_message(chat_id=chat_id, text=text)
#
#     return counter


async def send_message(chat_id: int, text: str, disable_notification: bool = False) -> int:
    from main import bot

    """
    Safe messages sender
    Обработчик ошибок при рассылке
    """
    try:
        await bot.send_message(chat_id, text, disable_notification=disable_notification, parse_mode='HTML',
                               disable_web_page_preview=True)
        return 1
    except Exception as e:
        logger.info(f"Target [ID:{chat_id}]: failed")
        return 0
