import os
from aiogram import types

from aiogram import Router, Bot
from utils.commands import set_commands

router_admin = Router()
admin_token = 739424080


async def start_bot(bot: Bot):
    """
    Handler for admin, that inform bot starting
    :param bot:
    :return:
    """

    await set_commands(bot)
    await bot.send_message(admin_token, text="Bot is start!",
                           reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[

                               types.InlineKeyboardButton(
                                   text='НАписать', callback_data='start_dialog_739424080'
                               )
                           ]]
                           )
                           )


async def stop_bot(bot: Bot):
    """
    Handler for admin, that inform bot stopping
    :param bot:
    :return:
    """
    await bot.send_message(admin_token, text="Bot is stop!")
