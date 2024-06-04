import asyncio
from main import dp
from utils import states_users as su
from aiogram import types, Router
from aiogram import F

from utils import states_users as s

cld = Router()



async def send_button_write_admin(call: types.CallbackQuery):
    """Отправка кнопки 'Написать администратору'"""
    await call.answer()
    await call.message.answer(
        'Если вы хотите забронировать больше, чем один стол — '
        'Вам нужно связаться с администратором.',
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[

            types.InlineKeyboardButton(
                text='Написать администратору', callback_data='write_admin'
            )
        ]]
        )
    )


async def req_text_question(call: types.CallbackQuery):
    """Запрашивает вопрос для админа"""
    await call.answer()
    await call.message.answer(
        'Пожалуйста, напишите, какой вопрос Вас интересует'
    )
    await su.set_state(call.from_user.id, 'question_for_admin')


async def send_question_admins(message: types.Message):
    """Отправка вопроса админам"""
    await su.get_state_user(
        message.from_user.id, reset=True, clear_data=True
    )
    await message.answer(
        'Наш администратор ответит Вам в ближайшее время.'
    )

    for admin_id in [739424080]:
        try:
            await dp.bot.send_message(
                chat_id=admin_id,
                text=(
                    f'<b>Сообщение от '
                    f'{message.from_user.id}'
                    f'</b>\n\n'
                    f'<i>{message.text}</i>'
                ),
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(
                    text='Начать диалог', callback_data=f'start_dialog_'
                                                        f'{message.from_user.id}'
                )]])
            )
        except:
            pass

        await asyncio.sleep(.05)


async def send_message_admin(message: types.Message):
    """Отправка сообщения админу"""
    admin_id = await su.get_data_from_state(
        message.from_user.id, 'dialog_with_admin'
    )
    await dp.bot.send_message(
        chat_id=admin_id,
        text=(
            f'<b>Сообщение от '
            f'{message.from_user.id}</b>\n\n'
            f'<i>{message.text}</i>'
        )
    )


cld.callback_query()
cld.message(send_message_admin, state='message_for_admin')
cld.message(send_question_admins, state='question_for_admin')
cld.callback_query(req_text_question, F('write_admin'))
cld.callback_query(send_button_write_admin, F('question_admin'))
