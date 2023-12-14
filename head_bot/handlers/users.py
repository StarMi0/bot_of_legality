from aiogram import Router, Bot, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.filters import CommandStart, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton

from utils.utils import check_registration
from utils.data import group_ID

router_users = Router()

select_service = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Юридическая консультация",
            callback_data="Legality_consult"
        )
    ],
    [
        InlineKeyboardButton(
            text="Автоюрист",
            callback_data="Auto_consult"
        )
    ],
    [
        InlineKeyboardButton(
            text="Юридический аудит",
            callback_data="Audit"
        )
    ],
    [
        InlineKeyboardButton(
            text="Общие вопросы",
            callback_data="All_consult"
        )
    ]
])


@router_users.message(CommandStart())
async def get_start(message: Message, bot: Bot):
    """
    Main start handler
    :param message:
    :param bot:
    :return:
    """
    # Проверяет пользователя на наличие регистрации
    user_id = message.from_user.id
    if not await check_registration(user_id):
        # Если пользователь не зарегистрирован, предлагаем пройти регистрацию
        reg_builder = InlineKeyboardBuilder()
        reg_builder.add(
            types.InlineKeyboardButton(
                text="Регистрация",
                url="http://yourwebsite.com/register"
            )
        )
        await message.reply("Вы не зарегистрированы. Пройдите регистрацию по ссылке:",
                            reply_markup=reg_builder.as_markup())
    else:

        await bot.send_message(message.from_user.id, f"<b>Hello, {message.from_user.first_name}! "
                                                     f"\nТут будет приветственное сообщение!</b>",
                               reply_markup=select_service)


"""
Ветка Юридическая консультация
"""


class Consult(StatesGroup):
    question = State()
    file_add = State()


@router_users.callback_query(F.data == "Legality_consult")
async def input_question(message: Message, state: FSMContext):
    await message.answer("Коротко опишите Ваш вопрос:")
    await state.set_state(Consult.question)


@router_users.message(StateFilter(Consult.question))
async def input_file(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Без файла",
        callback_data="send_to_chat")
    )
    await state.update_data(question=message.text)
    await message.answer("Отправьте необходимые файлы по Вашему вопросу. \n\nМожно отправить только один файл, "
                         "поэтому если у Вас есть несколько файлов, которыми вы хотели бы поделиться, "
                         "запакуйте их в архив.")

    await state.set_state(Consult.file_add)


@router_users.callback_query(F.data == "state_clear")
async def clear_state(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Чат окончен")
    await state.clear()


"""
Ветка Автоюрист
"""

"""
Ветка Юридический аудит
"""

"""
Ветка Общие вопросы
"""
