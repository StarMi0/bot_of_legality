from aiogram import Router, F, Bot
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message

from database.request import get_active_order, get_active_order_lawyer_id, get_order_info_by_order_id, end_order
from routers.states import EndOrder

router = Router(name=__name__)


@router.message(F.text == "Мои заказы")
async def send_active_orders(call: CallbackQuery, bot: Bot, state: FSMContext):
    user_id = call.from_user.id
    order_id = await get_active_order(user_id)
    lawyer_id = await get_active_order_lawyer_id(user_id, order_id)

    if order_id:
        if user_id == lawyer_id:
            # Исполнитель получает информацию по заказу и кнопку завершения заказа
            order_info = get_order_info_by_order_id(order_id)
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Завершить заказ", callback_data=f"complete_order_{order_id}")]]
            )
            await bot.send_message(chat_id=user_id, text=f"У вас имеется действующий заказ: {order_info}", reply_markup=keyboard)
            await state.set_state(EndOrder.SEND_FINAL_TEXT)
        else:
            if not lawyer_id:
                await bot.send_message(chat_id=user_id, text='Вы еще не выбрали исполнителя по заказу.')
            else:
                order_info = get_order_info_by_order_id(order_id)
                await bot.send_message(chat_id=user_id, text=f"У вас имеется действующий заказ: {order_info}")
    else:
        await call.answer("У вас нет активных заказов")


@ router.callback_query(F.data.startswith("complete_order_"))
async def complete_order(callback: CallbackQuery, bot: Bot, state: FSMContext):
    order_id = callback.data.split("_")[2]
    await bot.send_message(callback.from_user.id, "Введите описание выполненной работы.")
    await state.set_state(EndOrder.SEND_FINAL_TEXT)
    await state.update_data(order_id=order_id)


@router.message(EndOrder.SEND_FINAL_TEXT)
async def receive_final_text(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(final_text=message.text)
    await message.answer("Теперь отправьте файлы (если необходимо), затем нажмите 'Далее'.",
                         reply_markup=InlineKeyboardMarkup(
                             inline_keyboard=[[InlineKeyboardButton(text="Далее", callback_data="next_send_files")]]
                         ))
    await state.set_state(EndOrder.SEND_FINAL_FILES)


@router.message(EndOrder.SEND_FINAL_FILES, content_types=ContentType.ANY)
async def receive_final_files(message: Message, state: FSMContext):
    data = await state.get_data()
    files = data.get("files", [])
    files.append(message)
    await state.update_data(files=files)
    await message.answer("Файл принят. Отправьте ещё или нажмите 'Далее'.")


@router.callback_query(F.data == "next_send_files")
async def finalize_order(callback: CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    order_id = data.get("order_id")
    final_text = data.get("final_text")
    files = data.get("files", [])

    # Отправка заказчику
    customer_id = await get_active_order_lawyer_id(callback.from_user.id, order_id)
    await bot.send_message(customer_id, f"Исполнитель завершил работу по заказу {order_id}: {final_text}")
    for file in files:
        if file.photo:
            await bot.send_photo(customer_id, file.photo[-1].file_id)
        elif file.document:
            await bot.send_document(customer_id, file.document.file_id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Завершить заказ", callback_data=f"confirm_close_{order_id}")]]
    )
    await bot.send_message(customer_id, "Проверьте файлы и подтвердите завершение заказа.", reply_markup=keyboard)
    await callback.answer()


@ router.callback_query(F.data.startswith("confirm_close_"))
async def confirm_close(callback: CallbackQuery, bot: Bot):
    order_id = callback.data.split("_")[2]
    await end_order(order_id, "close")

    customer_id = callback.from_user.id
    lawyer_id = await get_active_order_lawyer_id(customer_id, order_id)

    await bot.send_message(lawyer_id, "Заказчик принял работу, заказ завершен.")
    await bot.send_message(customer_id, "Вы подтвердили завершение заказа.")
