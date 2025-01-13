import asyncio
import logging
import sys

from aiogram.fsm.storage.memory import MemoryStorage
from redis.asyncio import Redis
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand

from utils.config import *
from database.db_creation import create_tables_if_not_exists
from routers import router as main_router
from routers.users.admin import notify_admins_on_stop, notify_admins_on_start
from database.request import get_admins
from aiohttp import ClientTimeout
from database.redis_db import check_redis_connection

timeout = ClientTimeout(total=60)

"""Настраиваем логи"""
logger.add('logs/DEBUG.log', format="{time} {level} {message}", level="DEBUG", rotation="10 MB", compression="zip")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


async def setup_bot_and_dispatcher():
    """
    Настройка бота, базы данных, Redis и фильтров.
    """
    # Подключение к Redis
    redis = Redis(host=redis_host, port=redis_port)
    # Проверяем подключение к Redis
    if await check_redis_connection(redis_host, redis_port):
        print("Redis доступен. Запускаем бота...")
        # Здесь можно добавить запуск вашего бота
    else:
        print("Redis недоступен. Проверьте настройки.")
    storage = RedisStorage(redis=redis)

    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=storage)
    dp.include_router(main_router)

    # Установка команд бота
    bot_commands = [
        BotCommand(command="/start", description="Главное меню"),
    ]
    await bot.set_my_commands(bot_commands)

    # Создание таблиц базы данных, если они не существуют
    await create_tables_if_not_exists(my_host, my_user, my_password, my_database)

    admins = await get_admins()

    # Уведомление о старте
    await notify_admins_on_start(bot, admins)

    return bot, dp, redis, admins
    
    
async def main():
    """
    Основной запуск бота.
    """
    bot, dp, redis, admins = await setup_bot_and_dispatcher()
    try:
        logger.info("Бот запущен.")
        await dp.start_polling(bot)
    finally:
        logger.info("Остановка бота...")
        await notify_admins_on_stop(bot, admins)
        await redis.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Выход из программы.")
