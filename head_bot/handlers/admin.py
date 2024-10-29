import os

import loguru
from aiogram import Router, Bot
from aiogram.types import Message

from utils.commands import set_commands
from loguru import logger
router_admin = Router()
admin_token = 1165691824


async def start_bot(bot: Bot):
    """
    Handler for admin, that inform bot starting
    :param bot:
    :return:
    """
    await set_commands(bot)
    await bot.send_message(admin_token, text="Bot is start!")


async def stop_bot(bot: Bot):
    """
    Handler for admin, that inform bot stopping
    :param bot:
    :return:
    """
    await bot.send_message(admin_token, text="Bot is stop!")


async def get_chat(message: Message):
    """
    Handler for admin, that inform bot stopping
    :param bot:
    :return:
    """
    logger.info(message.chat.id)
    await message.delete()