import datetime

from aiogram import Router, Bot, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from database.models import Order, OrderInfo
from database.request import add_order, update_table, get_active_order, get_active_order_lawyer_id, add_user, \
    add_order_info, get_offers_by_order_id, get_order_additional_info_by_order_id, add_lawyer_info, \
    get_order_info_by_order_id
from handlers.registration import choose_role
from utils.callbackdata import BranchChoose, ConfirmOrDeleteOffer, GetResponse, GetAnswer
from utils.payments import create_payment_link
from utils.states import Consult
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardBuilder
from keyboard.kb import select_service_kb, get_main_user_kb, get_main_lawyer_kb
from utils.utils import check_registration, check_active_query
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
    # await add_user(message.from_user.id, message.from_user.username, 'user')
    if not role:
        await choose_role(message, bot)
        # Если пользователь не зарегистрирован, предлагаем пройти регистрацию
        # reg_builder = InlineKeyboardBuilder()
        # reg_builder.button(text="Регистрация", url="http://yourwebsite.com/register")
        #
        # await message.reply("Вы не зарегистрированы. Пройдите регистрацию по ссылке:",
        #                     reply_markup=reg_builder.as_markup())
    else:
        if role == 'user':
            kb = await get_main_user_kb()
            await bot.send_message(message.from_user.id, f"<b>Hello, {message.from_user.first_name}! "
                                                         f"\nТут будет приветственное сообщение!</b>",
                                   reply_markup=kb)
        elif role == 'lawyer':
            kb = await get_main_lawyer_kb()
            await bot.send_message(message.from_user.id, f"<b>Hello, {message.from_user.first_name}! "
                                                         f"\nТут будет приветственное сообщение!</b>",
                                   reply_markup=kb)
        elif role == 'admin':
            pass


async def registration_end_user(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    user_fio = data.get("FIO")
    user_date_birth = data.get("DATE")
    await add_user(user_id=call.from_user.id, user_name=call.from_user.username, user_fio=user_fio,
                   user_date_birth=user_date_birth, role='user')
    await state.clear()
    await send_select_service(call, bot)


async def registration_end_lawyer(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    education = data.get("EDUCATION")
    kb = await get_main_lawyer_kb()

    await add_lawyer_info(user_id=call.from_user.id, education=education)
    await state.clear()
    await bot.send_message(chat_id=call.from_user.id, text='Главное меню', reply_markup=kb)


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
    # kb.button(text="Без файла", callback_data="send_query_to_lawyers_chat")
    kb.button(text="Без файла", callback_data="go_confirm_query")
    kb.adjust(1)
    await state.update_data(question=message.text)
    await bot.send_message(chat_id=message.from_user.id,
                           text="Отправьте необходимые файлы по Вашему вопросу.", reply_markup=kb.as_markup())
    await state.set_state(Consult.additional_files)


async def process_file_to_lawyer(message: types.Message, bot: Bot, state: FSMContext):
    kb = InlineKeyboardBuilder()
    # kb.button(text='Отправить вопрос', callback_data='send_query_to_lawyers_chat')
    kb.button(text='Далее', callback_data='go_confirm_query')
    kb.button(text='Отмена', callback_data='cancel')
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
    # kb.button(text="Без файла", callback_data="send_query_to_lawyers_chat")
    kb.button(text="Без файла", callback_data="go_confirm_query")
    kb.adjust(1)
    await state.update_data(question=message.text)
    await bot.send_message(chat_id=message.from_user.id,
                           text="Отправьте необходимые файлы по Вашему вопросу.", reply_markup=kb.as_markup())
    await state.set_state(Consult.file_add)


async def process_file_from_user(message: types.Message, bot: Bot, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.button(text='Далее', callback_data='go_confirm_query')
    # kb.button(text='Отправить вопрос', callback_data='send_query_to_lawyers_chat')
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


async def send_query_to_confirm(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.button(text="Отправить", callback_data="send_query_to_lawyers_chat")
    await callback.answer()
    data = await state.get_data()
    group_id = data.get('group_id')
    files = data.get('files')
    question = data.get('question')
    user_id = callback.from_user.id
    if files:
        media_group = MediaGroupBuilder()
        for f in files[:-2]:
            media_group.add_document(media=f)
        media_group.add_document(media=files[-1], caption=question)
        await bot.send_media_group(chat_id=callback.from_user.id, media=media_group.build())
        await bot.send_message(chat_id=callback.from_user.id, text='Так выглядит ваш вопрос:',
                               reply_markup=kb.as_markup())
    else:
        await bot.send_message(chat_id=callback.from_user.id, text='Так выглядит ваш вопрос:',
                               reply_markup=kb.as_markup())
        await bot.send_message(chat_id=callback.from_user.id, text=question)


async def send_query_to_lawyers(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await callback.message.answer(text='Ваш вопрос отправлен!')
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
            msg = await bot.send_media_group(chat_id=group_id, media=media_group.build())
            message_ids = f"{','.join([str(i.message_id) for i in msg])}"
            msg = await bot.send_message(chat_id=group_id, text='Ответить',
                                         reply_markup=kb.as_markup())
            message_ids += f",{msg.message_id}"
        else:
            msg = await bot.send_message(chat_id=group_id, text=question, reply_markup=kb.as_markup())
            message_ids = f"{msg.message_id}"
            print(message_ids)
        await add_order_info(order_id=uniq_id, order_text=question, documents_id=files, order_cost=None,
                             order_day_start=None, order_day_end=None, message_id=message_ids, group_id=group_id)

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
            msg = await bot.send_media_group(chat_id=group_id, media=media_group.build())
            message_ids = f"{','.join([str(i.message_id) for i in msg])}"
            msg = await bot.send_message(chat_id=group_id, text='Ответить',
                                         reply_markup=kb.as_markup())
            message_ids += f",{msg.message_id}"
        else:
            msg = await bot.send_message(chat_id=group_id, text=question, reply_markup=kb.as_markup())
            message_ids = f"{msg.message_id}"
            print(message_ids)
        await add_order_info(order_id=uniq_id, order_text=question, documents_id=files, order_cost=None,
                             order_day_start=None, order_day_end=None, message_id=message_ids, group_id=group_id)

    await state.clear()


async def confirm_or_edith_query(message: Message, bot: Bot, state: FSMContext):
    pass


async def clear_state(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Чат окончен")
    await state.clear()


async def confirm_or_delete_offer(call: CallbackQuery, bot: Bot, callback_data: ConfirmOrDeleteOffer,
                                  state: FSMContext):
    from utils.PaymentChecker import sched
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    order_id = callback_data.order_id
    confirm = callback_data.confirm
    lawyer_id, develop_price, develop_time = await get_offers_by_order_id(order_id)
    # тут надо получить из бд айди сообщения из базы юристов и айди сообщения чтобы его удалить (закрыть заказ)
    # если кнопка подтвердить была
    # если отклонить то пишем юристу что ваше предложение отклонено
    if confirm:
        text = 'Необходимо оплатить стоимость заказа. Ссылка будет доступна 15 минут.'
        payment_url = create_payment_link(orderNumber=order_id, amount=develop_price)
        kb = InlineKeyboardBuilder()
        kb.button(text='Оплатить', url=payment_url)
        await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=kb.as_markup())
        end_time = datetime.datetime.now() + datetime.timedelta(minutes=15)
        end_time = end_time.strftime('%d.%m.%Y %H:%M:%S')
        job_name = f"{call.from_user.id}_{order_id}_{end_time}"

        # chat_id, message_id = await get_order_message_chat_id(order_id)
        # await bot.delete_message(chat_id=chat_id, message_id=message_id)

    else:
        await bot.send_message(chat_id=lawyer_id, text='Ваше предложение отклонили.')


async def on_success_payment(user_id: str, order_id: str):
    from main import bot
    lawyer_id, develop_price, develop_time = await get_offers_by_order_id(order_id)
    today_day = datetime.datetime.today().date()
    date_end = today_day + develop_time
    await update_table(Order.__tablename__,
                       field_values={'lawyer_id': lawyer_id, 'order_status': 'in_progress'},
                       where_clause={f'order_id': order_id})
    await update_table(OrderInfo.__tablename__, field_values={'order_cost': develop_price,
                                                              'order_day_start': today_day,
                                                              'order_day_end': date_end
                                                              },
                       where_clause={f'order_id': order_id})
    info = await get_order_additional_info_by_order_id(order_id)
    order_text, documents_id, order_cost, order_day_start, order_day_end, message_id, group_id = info

    await bot.send_message(chat_id=user_id, text='Заказ успешно оплачен!')
    await bot.send_message(chat_id=lawyer_id, text='Ваше предложение приняли.')
    for msg_id in message_id.split(','):
        kb = InlineKeyboardBuilder()
        kb.button(text='В работе.', callback_data='empty')
        await bot.forward_message(chat_id=lawyer_id, message_id=msg_id, from_chat_id=group_id)
        await bot.delete_message(chat_id=group_id, message_id=msg_id)

async def on_failure_payment(user_id: str, order_id: str):
    from main import bot
    await bot.send_message(chat_id=user_id, text='Заказ не был оплачен!')

async def on_client_lawyer_chat_start(call: CallbackQuery, bot: Bot, state: FSMContext):
    from main import dp
    kb = ReplyKeyboardBuilder()
    kb.button(text='Закончить чат')
    order_id = call.data.split('_')[-1]
    user_id, lawyer_id, status = await get_order_info_by_order_id(order_id)
    user_state = await dp.fsm.get_context(bot=bot, chat_id=user_id, user_id=user_id)
    lawyer_state = await dp.fsm.get_context(bot=bot, chat_id=lawyer_id, user_id=lawyer_id)
    await user_state.set_state(Consult.lawyer_client_chat)
    await lawyer_state.set_state(Consult.lawyer_client_chat)
    await lawyer_state.update_data(ORDER_ID=order_id)
    await user_state.update_data(ORDER_ID=order_id)
    await bot.send_message(chat_id=lawyer_id, text=f'Начат чат по поводу заказа {order_id}',
                           reply_markup=kb.as_markup(resize_keyboard=True))
    await bot.send_message(chat_id=user_id, text=f'Начат чат по поводу заказа {order_id}',
                           reply_markup=kb.as_markup(resize_keyboard=True))


async def end_chat(message: Message, bot: Bot, state: FSMContext):
    from main import dp
    data = await state.get_data()
    order_id = data.get('ORDER_ID')
    user_id, lawyer_id, status = await get_order_info_by_order_id(order_id)
    user_state = await dp.fsm.get_context(bot=bot, chat_id=user_id, user_id=user_id)
    lawyer_state = await dp.fsm.get_context(bot=bot, chat_id=lawyer_id, user_id=lawyer_id)
    await user_state.clear()
    await lawyer_state.clear()
    await bot.send_message(chat_id=lawyer_id, text=f'Чат окончен.',
                           reply_markup=ReplyKeyboardRemove())
    await bot.send_message(chat_id=user_id, text=f'Чат окончен.',
                           reply_markup=ReplyKeyboardRemove())


async def process_dialog(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    order_id = data.get('ORDER_ID')
    user_id, lawyer_id, status = await get_order_info_by_order_id(order_id)
    if message.from_user.id == user_id:
        await bot.forward_message(from_chat_id=user_id, chat_id=lawyer_id, message_id=message.message_id)
    elif message.from_user.id == lawyer_id:
        await bot.forward_message(from_chat_id=lawyer_id, chat_id=user_id, message_id=message.message_id)





"""
Ветка Автоюрист
"""

"""
Ветка Юридический аудит
"""

"""
Ветка Общие вопросы
"""
