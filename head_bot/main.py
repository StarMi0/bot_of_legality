import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from loguru import logger

import handlers

"""Настраиваем логи"""
logger.add('DEBUG.log', format="{time} {level} {message}", filter="my_module", level="ERROR")
logger.add('DEBUG.log', format="{time} {level} {message}", filter="my_module", level="INFO")
logger.add('DEBUG.log', format="{time} {level} {message}", filter="my_module", level="DEBUG")


db_config = {
    'host': os.environ["BOT_TOKEN"],
    'user': os.environ["BOT_TOKEN"],
    'password': os.environ["BOT_TOKEN"],
    'database': os.environ["BOT_TOKEN"],
}

async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - "
               "(%(filename)s).%(funcaname)s(%(lineno)d) - %(message)s"
    )
    TOKEN = os.environ["BOT_TOKEN"]
    # All handlers should be attached to the Router (or Dispatcher)
    dp = Dispatcher()
    # Add handlers by routers
    dp.include_router(handlers.admin.router_admin)
    dp.include_router(handlers.lawyers.router_lawyers)
    dp.include_router(handlers.users.router_users)
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
