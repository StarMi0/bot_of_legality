from aiogram import Router, Bot
from aiogram.types import Message

router_users = Router()


async def get_start(message: Message, bot: Bot):
    """
    Main start handler
    :param message:
    :param bot:
    :return:
    """
    await bot.send_message(message.from_user.id, f"<b>Hello, {message.from_user.first_name}! \nGlad to meet you!</b>")
    await message.answer(f"<s>Hello, {message.from_user.first_name}! \nGlad to meet you!</s>")
    await message.reply(f"<tg-spoiler>Hello, {message.from_user.first_name}! \nGlad to meet you!</tg-spoiler>")
