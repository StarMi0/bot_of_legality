from aiogram import Router, Bot, F
from aiogram.filters import BaseFilter, Command
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder
from loguru import logger

from database.request import get_lawyers, add_offer, get_active_order_by_lawyer, get_order_additional_info_by_order_id, \
    get_order_info_by_order_id, get_offers_by_lawyer_order_id, get_order_document, get_documents
from keyboard.kb import lawyer_keyboard
from utils.states import EndOrder

router = Router(name=__name__)


# Кастомный фильтр для проверки пользователей
class LawyerFilter(BaseFilter):
    """Фильтр для проверки, является ли пользователь зарегистрированным как пользователь."""

    async def __call__(self, message: Message) -> bool:
        LAWYERS_DB = await get_lawyers()  # Временный список пользователей
        return str(message.from_user.id) in LAWYERS_DB

"""
ОСНОВНОЙ ФУНКЦИОНАЛ
"""

@router.message(Command("start"), LawyerFilter())
async def get_start(message: Message, bot: Bot):
    """
    Main start handler
    :param message:
    :param bot:
    :return:
    """
    # Текст инструкции
    instruction = (
        "Добро пожаловать в нашего бота!\n\n"
        "Здесь вы можете:\n"
        "1. Обратиться в поддержку.\n"
        "3. Просмотреть свои заказы.\n\n"
        "Выберите нужный пункт меню ниже."
    )

    # Отправляем сообщение с инструкцией и клавиатурой
    await message.answer(instruction, reply_markup=lawyer_keyboard)


@router.message(F.text=="Мои заказы", LawyerFilter())
async def send_active_orders_to_lawyers(call: CallbackQuery, bot: Bot):
    """
    Проверяет на наличие заказов
    """
    order_id = await get_active_order_by_lawyer(call.from_user.id)
    lawyers_orders_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Завершить", callback_data=f"end_order_{order_id}")],
    ])

    if order_id:

        order_info = get_order_info_by_order_id(order_id)
        await bot.send_message(chat_id=call.from_user.id,
                               text=f'У вас уже имеется действующий заказ:\n{order_info}',
                               reply_markup=lawyers_orders_kb)
    else:
        await call.answer("У вас нет активных заказов")


"""
ВЕТКА ЗВЕРШЕНИЯ ЗАКАЗА
"""

@router.callback_query(F.data.startswith("end_order_"))
async def end_order_by_lawyer(callback: CallbackQuery, state: FSMContext):
    _, order_id = callback.data.split("_")

    # Сохраняем `order_id` в состоянии
    await state.update_data(order_id=order_id)

    await callback.message.answer(
        "Отправьте текст завершенного заказа (описание результата)."
    )
    await state.set_state(EndOrder.SEND_FINAL_TEXT)


@router.message(EndOrder.SEND_FINAL_TEXT)
async def receive_final_text(message: Message, state: FSMContext):
    # Сохраняем текст завершенного заказа
    await state.update_data(final_text=message.text)
    # Инлайн клавиатура для загрузки файлов
    file_upload_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Далее", callback_data="end_order_files")],
        [InlineKeyboardButton(text='Отмена', callback_data='cancel_end_order')],
    ])

    await message.answer("Теперь отправьте файлы, если это необходимо. "
                         "\nПосле загрузки всех файлов нажмите \n'Далее'",
                         reply_markup=file_upload_kb)
    await state.set_state(EndOrder.SEND_FINAL_FILES)


@router.message(EndOrder.SEND_FINAL_FILES)
async def process_file_to_user(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    files = data.get('files', [])
    file_upload_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Далее", callback_data="end_order_files")],
        [InlineKeyboardButton(text='Отмена', callback_data='cancel_end_order')],
    ])

    if message.document:
        files.append(message.document.file_id)
    elif message.photo:
        # Сохраняем файл самого крупного фото
        files.append(message.photo[-1].file_id)
    elif message.text:
        # Если это текст, сохраняем его как строку
        files.append(message.text)
    else:
        # Если сообщение другого типа, можно игнорировать или сохранить, как требуется
        await message.reply("Этот тип сообщения не поддерживается для загрузки.")
        return

    await state.update_data(files=files,
                            lawyer_id=message.from_user.id)

    await bot.send_message(chat_id=message.from_user.id,
                           text="Файл успешно загружен. Загрузите следующий или нажмите 'Далее'.",
                           reply_markup=file_upload_kb)


@router.message(F.data == "end_order_files")
async def receive_final_files(message: Message, bot: Bot, state: FSMContext):
    # Получаем данные из состояния
    data = await state.get_data()
    final_text = data.get("final_text")
    order_id = data.get("order_id")
    # Дополнительно сохраняем файлы (если есть)
    files = data.get("files", [])
    files.append(message)
    await state.update_data(files=files)

    # Установка статуса заказа
    order_status = "end"
    user_id = ""

    try:
        # Отправляем текст и файлы клиенту
        await message.bot.send_message(chat_id=user_id, text=final_text)
        # Пересылка файлов
        for file_id in files:
            try:
                if file_id.startswith("photo_"):  # Или используйте другой метод для определения типа
                    await bot.send_photo(user_id, file_id)
                else:
                    await bot.send_document(user_id, file_id)
            except Exception as e:
                print(f"Ошибка при отправке файла: {e}")
    except Exception as e:
        print(f"Ошибка при отправке сообщения о завершении заказа пользователю {user_id}: {e}")

    # Кнопки подтверждения/поддержки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Завершить заказ", callback_data=f"complete_order_{order_id}")],
        [InlineKeyboardButton(text="Написать в поддержку", callback_data=f"support_order_{order_id}")]
    ])
    await message.bot.send_message(chat_id=user_id, text="Вы можете завершить заказ или написать в поддержку.",
                                   reply_markup=keyboard)


@router.message.callback_query(F.data.startswith("complete_order_"))
async def complete_order_by_user(call: CallbackQuery, state: FSMContext):
    order_id = call.data.split("_")[1]


@router.message.callback_query(F.data.startswith("support_order_"))
async def support_order_by_user(call: CallbackQuery, state: FSMContext):
    order_id = call.data.split("_")[1]