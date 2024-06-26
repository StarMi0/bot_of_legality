import asyncio
import logging
import os
import sys
from utils.config import BOT_TOKEN
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from loguru import logger
from database.db_creation import create_tables_if_not_exists
import handlers
from handlers.register_routers import register_users, register_lawyers
from utils.payments import create_payment_link
from aiogram.fsm.storage.memory import MemoryStorage

"""Настраиваем логи"""
logger.add('DEBUG.log', format="{time} {level} {message}", filter="my_module", level="ERROR")
logger.add('DEBUG.log', format="{time} {level} {message}", filter="my_module", level="INFO")
logger.add('DEBUG.log', format="{time} {level} {message}", filter="my_module", level="DEBUG")

bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)

dp = Dispatcher(storage=MemoryStorage())


async def main() -> None:
    from utils.PaymentChecker import global_sched
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - "
               "(%(filename)s).%(funcaname)s(%(lineno)d) - %(message)s"
    )
    await global_sched()
    # All handlers should be attached to the Router (or Dispatcher)
    await create_tables_if_not_exists()
    await register_lawyers()
    await register_users()

    # Add handlers by routers
    dp.include_router(handlers.users.router_users)
    dp.include_router(handlers.admin.router_admin)
    dp.include_router(handlers.lawyers.router_lawyers)


    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
