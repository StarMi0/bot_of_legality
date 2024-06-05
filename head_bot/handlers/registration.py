import datetime
from aiogram.types import Message, CallbackQuery
from aiogram import Router, Bot, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.request import add_user, add_document
from utils.states import Consult


async def choose_role(message: Message, bot: Bot):
    text = 'Для начала работы с ботом вам нужно пройти регистрацию. Выберите свою роль:'
    kb = InlineKeyboardBuilder()
    kb.button(text='Пользователь', callback_data='registration_user')
    kb.button(text='Юрист', callback_data='registration_lawyer')
    kb.adjust(1)
    await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=kb.as_markup())


async def process_role(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()
    if call.data == 'registration_user':
        await state.update_data(ROLE='user')
    else:
        await state.update_data(ROLE='lawyer')
    text = 'Введите свое ФИО одной строкой через пробел:'
    kb = InlineKeyboardBuilder()
    kb.button(text='Назад', callback_data='back_choose_role')
    await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=kb.as_markup())
    await state.set_state(Consult.fio)


async def process_fio(message: Message | CallbackQuery, bot: Bot, state: FSMContext):
    if isinstance(message, Message):
        await state.update_data(FIO=message.text)
    else:
        await message.answer()
    text = f'{message.text}\nВведите свою дату рождения в формате: дд.мм.гггг:'
    kb = InlineKeyboardBuilder()
    data = await state.get_data()
    if data.get('ROLE') == 'user':
        kb.button(text='Назад', callback_data='registration_user')
    else:
        kb.button(text='Назад', callback_data='registration_lawyer')
    await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=kb.as_markup())
    await state.set_state(Consult.date_birth)


async def process_date_birth(message: Message | CallbackQuery, bot: Bot, state: FSMContext):
    if isinstance(message, Message):
        await state.update_data(DATE=message.text)
    else:
        await message.answer()
    data = await state.get_data()
    if data.get('ROLE') == 'user':
        kb = InlineKeyboardBuilder()
        kb.button(text='Назад', callback_data='registration_process_fio')
        kb.button(text='Далее', callback_data='end_reg_user')
        text = f'{message.text}\nРегистрация завершена!'
        await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=kb.as_markup())
    else:
        text = 'Введите название своего образования полностью:'
        kb = InlineKeyboardBuilder()
        kb.button(text='Назад', callback_data='registration_process_fio')
        await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=kb.as_markup())
        await state.set_state(Consult.education)


async def process_education(message: Message | CallbackQuery, bot: Bot, state: FSMContext):
    if isinstance(message, Message):
        await state.update_data(EDUCATION=message.text)
    else:
        await message.answer()
    text = (f'{message.text}\n')
    kb = InlineKeyboardBuilder()
    kb.button(text='Назад', callback_data='registration_date_birth')
    kb.button(text='Далее', callback_data='add_lawyer_to_db')

    await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=kb.as_markup())
    await state.set_state(Consult.education_documents)

async def add_lawyer_to_db(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    user_fio = data.get("FIO")
    user_date_birth = data.get("DATE")
    education = data.get("EDUCATION")
    await add_user(user_id=call.from_user.id, user_name=call.from_user.username, user_fio=user_fio,
                   user_date_birth=user_date_birth, role='lawyer')
    text = (f'Высылайте документы о своем образовании (дипломы, сертификаты и тд.)\n'
            f'Когда загрузите все документы - нажмите далее.')
    kb = InlineKeyboardBuilder()
    kb.button(text='Назад', callback_data='registration_date_birth')
    kb.button(text='Далее', callback_data='end_reg_lawyer')
    await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=kb.as_markup())


async def process_documents(message: Message, bot: Bot):
    file = message.document.file_id

    file_info = await bot.get_file(file)
    content = await bot.download_file(file_info.file_path)
    await add_document(message.from_user.id, content)
    await bot.send_message(chat_id=message.from_user.id, text='Документ добавлен!')