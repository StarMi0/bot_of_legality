from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder
from loguru import logger

from database.models import Order
from database.request import add_offer, get_active_order_by_lawyer, get_order_additional_info_by_order_id, \
    get_order_info_by_order_id, get_offers_by_lawyer_order_id, get_order_document, get_documents, update_table
from keyboard.kb import get_main_lawyer_kb
from utils.callbackdata import BranchChoose, GetResponse, ConfirmOrDeleteOffer, GoToDevelopTime
from utils.states import Consult
from utils.utils import generate_unique_identifier

router_lawyers = Router()


async def process_response(call: CallbackQuery, bot: Bot, callback_data: GetResponse, state: FSMContext):
    await call.answer()
    original_user_id = callback_data.user_id
    order_id = callback_data.uniq_id
    offer = await get_offers_by_lawyer_order_id(str(call.from_user.id), order_id)
    if offer:
        await call.message.answer(text='Вы уже откликались на этот заказ.')
    else:
        order_text, documents_ids, cost, day_start, day_end, message_ids, group_id, = await get_order_additional_info_by_order_id(
            order_id)
        # Получаем данные по заказу из бд: текст, файлы
        order_text, files = None, None  # await get_order_text_files(order_id, original_user_id)
        # # Отправляем юристу и говорим что он откликнулся на этот заказ
        for msg in message_ids.split(','):
            await bot.forward_message(from_chat_id=group_id, chat_id=call.from_user.id, message_id=msg)
        kb = InlineKeyboardBuilder()
        kb.button(text='Продолжить',
                  callback_data=GoToDevelopTime(order_id=order_id, original_user_id=original_user_id))
        await bot.send_message(chat_id=call.from_user.id, text='Вы откликнулись на заказ.', reply_markup=kb.as_markup())


async def go_to_develop_time_lawyer(call: CallbackQuery, callback_data: GoToDevelopTime, bot: Bot, state: FSMContext):
    await call.answer()
    original_user_id = callback_data.original_user_id
    order_id = callback_data.order_id
    await state.update_data(original_user_id=original_user_id, order_id=order_id)
    await state.set_state(Consult.develop_time)
    await bot.send_message(chat_id=call.from_user.id, text='Введите сроки работы в *днях*:', parse_mode='Markdown')


async def get_develop_time(message: Message, bot: Bot, state: FSMContext):
    develop_time = message.text
    if develop_time.isdigit():
        kb = InlineKeyboardBuilder()
        kb.button(text='Да', callback_data='go_to_price_lawyer')
        await bot.send_message(chat_id=message.from_user.id, text=f'Время работы над заказом: {develop_time}\n'
                                                                  f'Нажмите Да, если верно,'
                                                                  f'пришлите правильное время если нет.',
                               reply_markup=kb.as_markup())
        await state.update_data(develop_time=develop_time)
    else:
        await message.answer(text='Введите число в днях.')


async def confirm_develop_time(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()
    await state.set_state(Consult.price)
    await bot.send_message(chat_id=call.from_user.id, text='Введите точную цену работы в рублях без пробелов:')


async def get_develop_price(message: Message, bot: Bot, state: FSMContext):
    develop_price = message.text
    if develop_price.isdigit():
        kb = InlineKeyboardBuilder()
        kb.button(text='Да', callback_data='send_offer_to_client')
        await bot.send_message(chat_id=message.from_user.id, text=f'Цена работы: {develop_price}\n'
                                                                  f'Нажмите Да, если верно,'
                                                                  f'пришлите правильную цену.',
                               reply_markup=kb.as_markup())
        await state.update_data(develop_price=develop_price)
    else:
        await message.answer(text='Введите число в рублях.')


async def send_offer_to_client(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    original_user_id = data.get('original_user_id')
    develop_time = data.get('develop_time')
    develop_price = data.get('develop_price')
    order_id = data.get('order_id')
    lawyer_id = call.from_user.id
    kb = InlineKeyboardBuilder()
    await state.clear()
    print(original_user_id, develop_price, develop_time, order_id, lawyer_id)
    await call.message.answer(text='Предложение отправлено!')
    # Ниже получаем из бд инфу по юристу и суем ее в сообщение (а че там кроме рейтинга)
    lawyer_info = None  # await get_lawyer_info(lawyer_id)
    new_offer_id = await generate_unique_identifier()

    kb.button(text='Принять',
              callback_data=ConfirmOrDeleteOffer(offer_id=new_offer_id,
                                                 lawyer_id=str(lawyer_id), confirm=True))
    kb.button(text='Отклонить',
              callback_data=ConfirmOrDeleteOffer(offer_id=new_offer_id,
                                                 lawyer_id=str(lawyer_id), confirm=False))
    kb.button(text='Отменить заказ',
              callback_data=f'order_cancel_{order_id}')



    message_text = f'Предложение по вашему заказу:\n' \
                   f'Сроки: {develop_time}\n' \
                   f'Цена: {develop_price}\n' \
                   f'Рейтинг юриста: {lawyer_info}\n'
    await add_offer(new_offer_id, order_id, str(lawyer_id), order_cost=develop_price, develop_time=develop_time)
    await bot.send_message(chat_id=original_user_id, text=message_text, reply_markup=kb.as_markup())


async def get_active_orders_lawyer(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()
    orders = await get_active_order_by_lawyer(str(call.from_user.id))
    logger.info(orders)
    if orders:
        kb = InlineKeyboardBuilder()
        for i, order in enumerate(orders):
            kb.button(text=f'{i + 1}', callback_data=f'order_{order}')
        text = 'Выберите нужный заказ:'
        await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=kb.as_markup())
    else:
        await bot.send_message(chat_id=call.from_user.id,
                               text='Активных заказов нет',
                               reply_markup=await get_main_lawyer_kb())


async def send_order_info(call: CallbackQuery, bot: Bot, state: FSMContext):
    order_id = call.data.split('_')[-1]
    order_text, documents_ids, cost, day_start, day_end, _, _, = await get_order_additional_info_by_order_id(order_id)
    logger.info(order_text, documents_ids)
    text = (f'{order_text}\n'
            f'Цена: {cost}\n'
            f'Дата начала: {day_start}\n'
            f'До: {day_end}\n')
    docs = MediaGroupBuilder()
    for d in documents_ids:
        docs.add_document(d)
    kb = InlineKeyboardBuilder()
    kb.button(text='Главное меню', callback_data='main_lawyer')
    kb.button(text='Написать заказчику', callback_data=f'question_lawyer_{order_id}')
    kb.button(text='Закрыть заказ', callback_data=f'close_order_{order_id}')
    kb.adjust(1)
    await call.message.answer(text=text, reply_markup=kb.as_markup())
    if docs:
        await bot.send_media_group(chat_id=call.from_user.id, media=docs.build())


async def send_main_lawyer_kb(call: CallbackQuery, bot: Bot, state: FSMContext):
    kb = await get_main_lawyer_kb()
    await bot.send_message(call.from_user.id, f"<b>Hello, {call.from_user.first_name}! "
                                              f"\nТут будет приветственное сообщение!</b>",
                           reply_markup=kb)


async def on_lawyer_client_chat_start(call: CallbackQuery, bot: Bot, state: FSMContext):
    from main import dp
    kb = ReplyKeyboardBuilder()
    kb.button(text='Закончить чат')
    order_id = call.data.split('_')[-1]
    user_id, lawyer_id, status = await get_order_info_by_order_id(order_id)
    user_state = StorageKey(bot_id=bot.id, chat_id=int(user_id), user_id=int(user_id))
    lawyer_state = StorageKey(bot_id=bot.id, chat_id=int(lawyer_id), user_id=int(lawyer_id))
    await dp.storage.set_state(key=user_state, state=Consult.lawyer_client_chat)
    await dp.storage.set_state(key=lawyer_state, state=Consult.lawyer_client_chat)
    await dp.storage.update_data(key=user_state, data={"ORDER_ID": order_id})
    await dp.storage.update_data(key=lawyer_state, data={"ORDER_ID": order_id})
    logger.error(user_state)
    logger.error(await dp.storage.get_data(key=lawyer_state))

    await bot.send_message(chat_id=lawyer_id, text=f'Начат чат по поводу заказа {order_id}',
                           reply_markup=kb.as_markup(resize_keyboard=True))
    await bot.send_message(chat_id=user_id, text=f'Начат чат по поводу заказа {order_id}',
                           reply_markup=kb.as_markup(resize_keyboard=True))


async def on_end_order(call: CallbackQuery, bot: Bot, state: FSMContext):
    order_id = call.data.split('_')[-1]
    await state.update_data(ORDER_ID=order_id)
    kb = InlineKeyboardBuilder()
    kb.button(text='Отмена', callback_data='main_lawyer')
    kb.button(text='Закрыть', callback_data=f'confirm_close_{order_id}')
    text = 'Вы уверены что хотите закрыть заказ?'
    await call.message.answer(text=text, reply_markup=kb.as_markup())


async def after_confirm_close(call: CallbackQuery, bot: Bot, state: FSMContext):
    text = 'Высылайте все документы по заказу.'
    await state.set_state(Consult.get_end_info)
    await call.message.answer(text=text)


async def on_get_end_info(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    order_id = data.get('ORDER_ID')

    if message.document:
        document_id = message.document.file_id
        res = await get_order_document(document_id, order_id)
        if res != 0:
            await message.answer('Что то пошло не так..')
        else:
            kb = InlineKeyboardBuilder()
            kb.button(text='Закрыть заказ', callback_data=f'full_close_{order_id}')
            await message.answer('Документ добавлен!', reply_markup=kb.as_markup())

    else:
        await message.answer('Нужно высылать информацию в виде документов .docx, .pdf')


async def on_full_end(call: CallbackQuery, bot: Bot, state: FSMContext):
    order_id = call.data.split('_')[-1]
    documents = await get_documents(order_id)
    user_id, lawyer_id, status = await get_order_info_by_order_id(order_id)
    media = MediaGroupBuilder(caption='Документы по вашему заказу.')
    for doc in documents:
        media.add_document(media=doc)
    kb = InlineKeyboardBuilder()
    kb.button(text='Закрыть заказ', callback_data=f'user_confirm_end_{order_id}')
    kb.button(text='Оспорить заказ', callback_data=f'user_dispute_end_{order_id}')
    text = ('Юрист закончил работу с вашим заказом, передаем вам все документы.\n Вы можете ознакомиться с ними и '
            'закрыть заказ,'
            'либо оспорить его, если вас не устроила работа. Через 7 дней заказ будет автоматически закрыт.')
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb.as_markup())
    await bot.send_media_group(chat_id=user_id, media=media.build())

    text_to_lawyer = 'Передали информацию клиенту, сообщим вам когда он примет решение по заказу.'
    await call.message.answer(text=text_to_lawyer)
    # await update_table(Order,
    #                    field_values={'order_status': 'in_progress'},
    #                    where_clause={f'order_id': order_id})

