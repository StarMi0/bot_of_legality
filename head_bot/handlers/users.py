import datetime

from aiogram import Router, Bot, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from database.request import add_order, update_table, get_active_order, get_active_order_lawyer_id
from utils.callbackdata import BranchChoose, ConfirmOrDeleteOffer, GetResponse, GetAnswer
from utils.states import Consult
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton
from keyboard.kb import select_service_kb, get_main_user_kb
from utils.utils import check_registration
from utils.config import group_ID

from utils.utils import generate_unique_identifier

router_users = Router()


async def get_start(message: Message, bot: Bot):
    """
    Main start handler
    :param message:
    :param bot:
    :return:
    """
    # Проверяет пользователя на наличие регистрации
    user_id = message.from_user.id
    role = await check_registration(user_id)
    if not role:
        # Если пользователь не зарегистрирован, предлагаем пройти регистрацию
        reg_builder = InlineKeyboardBuilder()
        reg_builder.button(text="Регистрация", url="http://yourwebsite.com/register")

        await message.reply("Вы не зарегистрированы. Пройдите регистрацию по ссылке:",
                            reply_markup=reg_builder.as_markup())
    else:
        if role == 'user':
            kb = await get_main_user_kb()
            await bot.send_message(message.from_user.id, f"<b>Hello, {message.from_user.first_name}! "
                                                     f"\nТут будет приветственное сообщение!</b>",
                               reply_markup=kb)
        elif role == 'lawyer':
            pass
        elif role == 'admin':
            pass
"""
Ветка Юридическая консультация
"""

async def send_select_service(call: CallbackQuery, bot: Bot):
    await bot.send_message(chat_id=call.from_user.id, text='Выберите тип услуг:', reply_markup=select_service_kb)


async def send_active_orders(call: CallbackQuery, bot: Bot, state: FSMContext):
    order_id = await get_active_order(call.from_user.id)
    lawyer_id = await get_active_order_lawyer_id(call.from_user.id)
    if order_id:
        if not lawyer_id:
            await bot.send_message(chat_id=call.from_user.id,
                                   text='Вы еще не выбрали исполнителя по заказу.',
                                   reply_markup=await get_main_user_kb())
        await bot.send_message(chat_id=call.from_user.id,
                               text='Введите вопрос по заказу:')
        await state.update_data(group_id=lawyer_id)
        await state.set_state(Consult.question_to)
    else:
        await bot.send_message(chat_id=call.from_user.id,
                               text='Активных заказов нет',
                               reply_markup=await get_main_user_kb())

async def process_branch(call: CallbackQuery, bot: Bot, callback_data: BranchChoose, state: FSMContext):
    await call.answer()
    await state.update_data(group_id=group_ID.get(callback_data.branch))
    await bot.send_message(chat_id=call.from_user.id, text="Коротко опишите Ваш вопрос:")
    await state.set_state(Consult.question)


async def process_input_question_to_lawyer(message: Message, bot: Bot, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.button(text="Без файла", callback_data="send_query_to_lawyers_chat")
    kb.adjust(1)
    await state.update_data(question=message.text)
    await bot.send_message(chat_id=message.from_user.id,
                           text="Отправьте необходимые файлы по Вашему вопросу.", reply_markup=kb.as_markup())
    await state.set_state(Consult.additional_files)


async def process_file_to_lawyer(message: types.Message, bot: Bot, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.button(text='Отправить вопрос', callback_data='send_query_to_lawyers_chat')
    # Process the file and add it to the data stored in the state
    file_id = message.document.file_id
    file_unique_id = message.document.file_unique_id
    file_name = message.document.file_name
    # Add your logic to handle the file, for example, store it in the state
    # file_data = {"file_id": file_id, "file_unique_id": file_unique_id, "file_name": file_name}
    data = await state.get_data()

    files = data.get('files')
    if files:
        files.append(file_id)
    else:
        files = [file_id]
    await state.update_data(files=files)

    await bot.send_message(chat_id=message.from_user.id,
                           text=f"Файл '{file_name}' добавлен. Можете добавить еще или подтвердить вопрос.",
                           reply_markup=kb.as_markup())


async def process_input_file(message: Message, bot: Bot, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.button(text="Без файла", callback_data="send_query_to_lawyers_chat")
    kb.adjust(1)
    await state.update_data(question=message.text)
    await bot.send_message(chat_id=message.from_user.id,
                           text="Отправьте необходимые файлы по Вашему вопросу.", reply_markup=kb.as_markup())
    await state.set_state(Consult.file_add)


async def process_file_from_user(message: types.Message, bot: Bot, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.button(text='Отправить вопрос', callback_data='send_query_to_lawyers_chat')
    # Process the file and add it to the data stored in the state
    file_id = message.document.file_id
    file_unique_id = message.document.file_unique_id
    file_name = message.document.file_name
    # Add your logic to handle the file, for example, store it in the state
    # file_data = {"file_id": file_id, "file_unique_id": file_unique_id, "file_name": file_name}
    data = await state.get_data()

    files = data.get('files')
    if files:
        files.append(file_id)
    else:
        files = [file_id]
    await state.update_data(files=files)

    await bot.send_message(chat_id=message.from_user.id,
                           text=f"Файл '{file_name}' добавлен. Можете добавить еще или подтвердить вопрос.",
                           reply_markup=kb.as_markup())


# async def delete_file(callback: types.CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     files = data.get("files", [])
#
#     await state.update_data(files=updated_files)
#
#     await callback.message.answer("Файл удален. Можете добавить еще или подтвердить вопрос.")


async def send_query_to_lawyers(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    group_id = data.get('group_id')
    files = data.get('files')
    question = data.get('question')
    user_id = callback.from_user.id

    # Добавить тут запись в базу данных вопроса и файлов
    if not await check_active_query(callback.from_user.id):
        uniq_id = await generate_unique_identifier()
        await add_order(order_id=uniq_id, user_id=user_id, lawyer_id=None, order_status='in_search', group_id=group_id)
        kb = InlineKeyboardBuilder()
        kb.button(text='Откликнуться', callback_data=GetResponse(uniq_id=uniq_id, user_id=user_id))
        if files:
            media_group = MediaGroupBuilder()
            for f in files[:-2]:
                media_group.add_document(media=f)
            media_group.add_document(media=files[-1], caption=question)
            await bot.send_media_group(chat_id=group_id, media=media_group.build())
            await bot.send_message(chat_id=group_id, text='Чтобы откликнуться на заказ выше⬆',
                                   reply_markup=kb.as_markup())
        else:
            await bot.send_message(chat_id=group_id, text=question, reply_markup=kb.as_markup())
    await state.clear()

async def send_question_to_lawyer(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    group_id = data.get('group_id')
    files = data.get('files')
    question = data.get('question')
    user_id = callback.from_user.id

    # Добавить тут запись в базу данных вопроса и файлов
    if not await check_active_query(callback.from_user.id):
        uniq_id = await generate_unique_identifier()
        await add_order(order_id=uniq_id, user_id=user_id, lawyer_id=None, order_status='in_search', group_id=group_id)
        kb = InlineKeyboardBuilder()
        kb.button(text='Ответить', callback_data=GetAnswer(order_id=uniq_id, user_id=user_id))
        if files:
            media_group = MediaGroupBuilder()
            for f in files[:-2]:
                media_group.add_document(media=f)
            media_group.add_document(media=files[-1], caption=question)
            await bot.send_media_group(chat_id=group_id, media=media_group.build())
            await bot.send_message(chat_id=group_id, text='Ответить',
                                   reply_markup=kb.as_markup())
        else:
            await bot.send_message(chat_id=group_id, text=question, reply_markup=kb.as_markup())
    await state.clear()

async def confirm_or_edith_query(message: Message, bot: Bot, state: FSMContext):
    pass


async def clear_state(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Чат окончен")
    await state.clear()





async def confirm_or_delete_offer(call: CallbackQuery, bot: Bot, callback_data: ConfirmOrDeleteOffer,
                                  state: FSMContext):
    order_id = callback_data.order_id
    # user_id = callback_data.user_id
    lawyer_id = callback_data.lawyer_id
    confirm = callback_data.confirm
    # тут надо получить из бд айди сообщения из базы юристов и айди сообщения чтобы его удалить (закрыть заказ)
    # если кнопка подтвердить была
    # если отклонить то пишем юристу что ваше предложение отклонено
    if confirm:
        # chat_id, message_id = await get_order_message_chat_id(order_id)
        # await bot.delete_message(chat_id=chat_id, message_id=message_id)
        today_day = datetime.datetime.today().date()
        await update_table(table_name='orders',
                           field_values={'lawyer_id': lawyer_id, 'order_status': 'in_progress'},
                           where_clause=f'order_id={order_id}')
        await update_table(table_name='orders_info', field_values={'order_cost': develop_price,
                                                                   'order_day_start': today_day,
                                                                   'order_day_end': today_day + develop_time},
                           where_clause=f'order_id={order_id}')
        await bot.send_message(chat_id=lawyer_id, text='Ваше предложение приняли.')
    else:
        await bot.send_message(chat_id=lawyer_id, text='Ваше предложение отклонили.')


"""
Ветка Автоюрист
"""

"""
Ветка Юридический аудит
"""

"""
Ветка Общие вопросы
"""

