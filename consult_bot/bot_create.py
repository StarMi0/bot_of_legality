from dotenv import find_dotenv, load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
from loguru import logger

load_dotenv(find_dotenv())
BOT_TOKEN = os.environ.get('BOT_TOKEN')
PAYMENT_TOKEN = os.environ.get('PAYMENT_TOKEN')
OUTLINE_KEY = os.environ.get('OUTLINE_KEY')

"""Создаем экземпляр бота и диспетчера"""
bot = Bot(token=BOT_TOKEN)

dp = Dispatcher(bot, storage=MemoryStorage())

"""При запуске программы выводим сообщение"""
async def on_startup(_):
    logger.info('Telegram bot is online')











