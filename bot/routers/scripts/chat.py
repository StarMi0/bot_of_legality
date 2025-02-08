from aiogram import Router, Bot, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.request import for_chat_id
from routers.states import *

router = Router(name=__name__)

"""
ВЕТКА ПЕРЕПИСОК
"""

@router.message(
    F.chat.type == "private",
    ~StateFilter(  # Исключаем все состояния, при которых переписка не должна работать
        Registration.fio,
        Registration.date_birth,
        Registration.education,
        Registration.upload_documents,
        Registration.data_to_admin,
        SupportStates.waiting_for_problem_description,
        Consult.CHOOSE_TOPIC,
        Consult.DESCRIBE_PROBLEM,
        Consult.UPLOAD_FILES,
        LawyerResponse.ENTER_PRICE,
        LawyerResponse.ENTER_DEADLINE,
        PaymentResponse.CONFIRM_RESPONSE,
        PaymentResponse.AWAITING_PAYMENT,
        EndOrder.SEND_FINAL_TEXT,
        EndOrder.SEND_FINAL_FILES,
        EndOrder.MESSAGE_TO_ADMIN,
    )
)
async def handle_message(message: Message, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    print(f"[LOG] Текущее состояние пользователя: {current_state}")

    user_id = str(message.from_user.id)
    chat_info = await for_chat_id(user_id)

    if not chat_info:
        await message.answer("У вас нет активных заказов")
        return

    to_id = chat_info["to_id"]
    if not to_id:
        await message.answer("Не выбран исполнитель по заказу")
        return

    # Пересылаем сообщение
    if message.text:
        await bot.send_message(chat_id=to_id, text=message.text)
    elif message.photo:
        await bot.send_photo(chat_id=to_id, photo=message.photo[-1].file_id, caption=message.caption)
    elif message.document:
        await bot.send_document(chat_id=to_id, document=message.document.file_id, caption=message.caption)
    else:
        await message.answer("Неподдерживаемый тип сообщения")