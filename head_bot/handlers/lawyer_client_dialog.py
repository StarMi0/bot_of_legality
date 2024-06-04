from aiogram import types, F, Bot, Dispatcher
from aiogram import Router
from utils import states_users as su
from main import dp

lcd = Router()



async def req_text_answer(call: types.CallbackQuery):
    """Запрашивает текст ответа"""
    await call.answer()

    client_id = int(call.data.split('_')[-1])
    await su.save_data_state(chat_id=client_id)
    await su.set_state(client_id, 'message_for_admin')
    await su.save_data_state(
        client_id, dialog_with_admin=call.from_user.id
    )
    await call.message.delete_reply_markup()
    await call.message.answer(
        'Отправьте текст сообщения',
        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[

            types.KeyboardButton(text='Завершить диалог')
        ]])
    )
    await su.set_state(call.from_user.id, 'answer_for_client')


async def send_answer_client(message: types.Message):
    """Отправка ответа клиенту"""
    client_id = await su.get_data_from_state(
        message.from_user.id, 'dialog_with_client'
    )
    await message.send_message(
        chat_id=client_id,
        text=(
            '<b>Сообщение от администратора:</b>\n\n'
            f'<i>{message.text}</i>\n\n'
            f'Отправьте ответ'
        )
    )


lcd.callback_query(req_text_answer, F(startswith='start_dialog_'))
lcd.messages(send_answer_client, state='answer_for_client')