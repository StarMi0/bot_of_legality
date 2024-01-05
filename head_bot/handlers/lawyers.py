from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.callbackdata import BranchChoose, GetResponse, ConfirmOrDeleteOffer
from utils.states import Consult

router_lawyers = Router()


async def process_response(call: CallbackQuery, bot: Bot, callback_data: GetResponse, state: FSMContext):
    await state.set_state(Consult.develop_time)
    original_user_id = callback_data.user_id
    order_id = callback_data.uniq_id
    await state.update_data(original_user_id=original_user_id, order_id=order_id)
    # Получаем данные по заказу из бд: текст, файлы
    # order_text, files = None, None#await get_order_text_files(order_id, original_user_id)
    # # Отправляем юристу и говорим что он откликнулся на этот заказ
    await bot.send_message(chat_id=call.from_user.id, text='Вы откликнулись на заказ.')
    # await bot.forward_message(chat_id=call.from_user.id,
    #                           from_chat_id=call.message.chat.id,
    #                           message_id=call.message.message_id)
    await bot.send_message(chat_id=call.from_user.id, text='Введите примерные сроки работы:')


@router_lawyers.message(F.text, StateFilter(Consult.develop_time))
async def get_develop_time(message: Message, bot: Bot, state: FSMContext):
    develop_time = message.text
    kb = InlineKeyboardBuilder()
    kb.button(text='Да', callback_data='go_to_price_lawyer')
    await bot.send_message(chat_id=message.from_user.id, text=f'Время работы над заказом: {develop_time}\n'
                                                              f'Нажмите Да, если верно,'
                                                              f'пришлите правильное время если нет.',
                           reply_markup=kb.as_markup())
    await state.update_data(develop_time=develop_time)


async def confirm_develop_time(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(Consult.price)
    await bot.send_message(chat_id=call.from_user.id, text='Введите точную цену работы:')


async def get_develop_price(message: Message, bot: Bot, state: FSMContext):
    develop_price = message.text
    kb = InlineKeyboardBuilder()
    kb.button(text='Да', callback_data='send_offer_to_client')
    await bot.send_message(chat_id=message.from_user.id, text=f'Цена работы: {develop_price}\n'
                                                              f'Нажмите Да, если верно,'
                                                              f'пришлите правильную цену.', reply_markup=kb.as_markup())
    await state.update_data(develop_price=develop_price)


async def send_offer_to_client(call: CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    original_user_id = data.get('original_user_id')
    develop_time = data.get('develop_time')
    develop_price = data.get('develop_price')
    order_id = data.get('order_id')
    lawyer_id = call.from_user.id
    kb = InlineKeyboardBuilder()
    # Ниже получаем из бд инфу по юристу и суем ее в сообщение (а че там кроме рейтинга)
    lawyer_info = None  # await get_lawyer_info(lawyer_id)
    kb.button(text='Принять',
              callback_data=ConfirmOrDeleteOffer(order_id=order_id, user_id=original_user_id,
                                                 lawyer_id=lawyer_id, confirm=True))
    kb.button(text='Отклонить',
              callback_data=ConfirmOrDeleteOffer(order_id=order_id, user_id=original_user_id,
                                                 lawyer_id=lawyer_id, confirm=True))
    message_text = f'Предложение по вашему заказу:' \
                   f'Сроки: {develop_time}' \
                   f'Цена: {develop_price}' \
                   f'Рейтинг юриста: {lawyer_info}'

    await bot.send_message(chat_id=original_user_id, text=message_text, reply_markup=kb.as_markup())
