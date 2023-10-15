import os
from aiogram import Router, Bot
from utils.commands import set_commands

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
