from aiogram import executor
from Telegramm import handler_user, handler_admin
from bot_create import on_startup, dp
from db.database import add_subscription, add_admin_to_db
from db.temp_subs import get_is_used_by_user_id, clear_temp_sub
from functions.checking_subs_time import create_checking_scheduler
from loguru import logger

from functions.vpn_key import create_vpn_key

"""Регистрируем хендлеры для админов и юзеров"""

handler_admin.register_handler_admin(dp)
handler_user.register_handler_client(dp)
"""Настраиваем логи"""

logger.add('DEBUG.log', format="{time} {level} {message}", filter="my_module", level="ERROR")
logger.add('DEBUG.log', format="{time} {level} {message}", filter="my_module", level="INFO")
logger.add('DEBUG.log', format="{time} {level} {message}", filter="my_module", level="DEBUG")


if __name__ == "__main__":
    """Запускаем в фоне проверку подписок и запускаем самого бота"""
    create_checking_scheduler()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

#
# async def main():
#     from db.temp_subs import set_used
#     await set_used(739424080)
#     a = await get_is_used_by_user_id(739424080)
#     print(a)
#
#
# if __name__=='__main__':
#     import asyncio
#     asyncio.run(main())
