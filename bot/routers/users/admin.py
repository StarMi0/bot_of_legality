from aiogram import Router, types
from aiogram.filters import BaseFilter, Command
from aiogram.types import Message

from database.request import get_admins

router = Router(name=__name__)


# Кастомный фильтр для проверки администратора
class AdminFilter(BaseFilter):
    """Фильтр для проверки, является ли пользователь администратором."""

    async def __call__(self, message: Message) -> bool:
        ADMINS_DB = await get_admins()
        return str(message.from_user.id) in ADMINS_DB


@router.message(Command("stats"), AdminFilter())
async def admin_stats_handler(message: types.Message):
    """Хэндлер для получения статистики"""
    await message.reply("Вот ваша статистика: ...")
    # Останавливаем дальнейшую обработку


@router.message(Command("help"), AdminFilter())
async def admin_help_handler(message: types.Message):
    """Хэндлер помощи для администраторов"""
    await message.reply("Список доступных команд: ...")
    # Останавливаем дальнейшую обработку


async def notify_admins_on_start(bot, admins: list[int]):
    """Оповещает администраторов о запуске бота"""
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, "Бот успешно запущен!")
        except Exception as e:
            print(f"Ошибка при отправке сообщения администратору {admin_id}: {e}")


async def notify_admins_on_stop(bot, admins: list[int]):
    """Оповещает администраторов об остановке бота"""
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, "Бот остановлен.")
        except Exception as e:
            print(f"Ошибка при отправке сообщения администратору {admin_id}: {e}")


# async def get_chat(message: Message):
#     """
#     Handler for admin, that inform bot stopping
#     :param bot:
#     :return:
#     """
#     logger.info(message.chat.id)
#     await message.delete()