import os
import uuid
from datetime import datetime, timedelta

from aiogram import Router, Bot, F
from aiogram.filters import BaseFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, \
    InputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.request import add_order, get_active_order, get_active_order_lawyer_id, \
    get_users, get_admins, get_active_order_and_partner, \
    get_order_info_by_order_id, add_order_info, \
    save_message
from keyboard.kb import user_keyboard
from loguru import logger
from routers.states import SupportStates, Consult, LawyerResponse, PaymentResponse, DialogState
from utils.config import group_ID as lawyers_group

router = Router(name=__name__)


# Кастомный фильтр для проверки пользователей
class UserFilter(BaseFilter):
    """Фильтр для проверки, является ли пользователь зарегистрированным как пользователь."""

    async def __call__(self, message: Message) -> bool:
        USERS_DB = await get_users()  # Временный список пользователей
        return str(message.from_user.id) in USERS_DB


@router.message(F.text == "/id")
async def get_chat_id(message: Message):
    chat_id = message.chat.id
    await message.answer(f"ID чата: {chat_id}")


@router.message(Command("start"), UserFilter())
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
        "2. Создать новый заказ.\n"
        "3. Просмотреть свои заказы.\n\n"
        "Выберите нужный пункт меню ниже."
    )

    # Отправляем сообщение с инструкцией и клавиатурой
    await message.answer(instruction, reply_markup=user_keyboard)

"""
Ветка Поддержка
"""


# Обработчик кнопки "Поддержка"
@router.message(F.text=="Поддержка", UserFilter())
async def start_support(message: Message, state: FSMContext):
    """
    Начало работы с поддержкой.
    """
    await message.answer(
        "Пожалуйста, опишите вашу проблему текстовым сообщением. Администратор свяжется с вами.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(SupportStates.waiting_for_problem_description)


# Обработчик ввода сообщения с проблемой
@router.message(SupportStates.waiting_for_problem_description)
async def receive_problem_description(message: Message, bot: Bot, state: FSMContext):
    """
    Получает описание проблемы от пользователя и отправляет администраторам.
    """
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
    problem_description = message.text

    admin_ids = await get_admins()
    # Формируем сообщение для администраторов
    admin_message = (
        f"🆘 Новое сообщение в поддержку:\n\n"
        f"👤 Пользователь: {full_name} (@{username})\n"
        f"🔗 Telegram: tg://user?id={user_id}\n\n"
        f"📄 Описание проблемы:\n{problem_description}"
    )

    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id, admin_message)
        except Exception as e:
            print(f"Не удалось отправить сообщение администратору {admin_id}: {e}")

    # Ответ пользователю
    await message.answer(
        "Ваше сообщение отправлено в техническую поддержку. Мы свяжемся с вами в ближайшее время."
    )
    await state.clear()


"""
Ветка Юридическая консультация
"""

@router.message(F.text=="Создать заказ", UserFilter())
async def send_active_orders(call: CallbackQuery, bot: Bot, state: FSMContext):
    """
    Проверяет на наличие заказов, если таковых нет, создает
    """
    order_id = await get_active_order(call.from_user.id)
    lawyer_id = await get_active_order_lawyer_id(call.from_user.id, order_id)
    if order_id:
        if not lawyer_id:
            """
            Если исполнитель по существующему заказу не выбран
            """
            await bot.send_message(chat_id=call.from_user.id,
                                   text='Вы еще не выбрали исполнителя по заказу.')
        else:
            """
            Вывод информации по текущему заказу
            """
            order_info = get_order_info_by_order_id(order_id)
            await bot.send_message(chat_id=call.from_user.id,
                                   text=f'У вас уже имеется действующий заказ:\n{order_info}')
    else:
        choose_topic_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Юридическая консультация", callback_data="topic_legal_advice")],
            [InlineKeyboardButton(text="Авто юристы", callback_data="topic_auto_advice")],
            [InlineKeyboardButton(text="Юристы по гражданским делам", callback_data="topic_civil_cases")],
            [InlineKeyboardButton(text="Юристы", callback_data="topic_lawyers")],
            [InlineKeyboardButton(text="Судебно правовые заключения", callback_data="topic_legal_opinions")],
            [InlineKeyboardButton(text="Адвокаты", callback_data="topic_lawyers")],
            [InlineKeyboardButton(text="Юридический аудит", callback_data="topic_legal_audit")],
        ])

        await call.answer("Выберите раздел:", reply_markup=choose_topic_kb)
        await state.set_state(Consult.CHOOSE_TOPIC)


# Обработчик отмены заказа
@router.callback_query(F.data=="cancel_order", UserFilter())
async def cancel_order(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Создание заказа отменено.")
    await state.clear()


# Обработчик выбора раздела
@router.callback_query(F.data.startswith("topic_"))
async def choose_topic(callback: CallbackQuery, state: FSMContext):
    topic = callback.data.split("_")[1]  # Получаем тему из callback_data
    await state.update_data(topic=topic)

    await callback.message.edit_text("Опишите вашу ситуацию:")
    await state.set_state(Consult.DESCRIBE_PROBLEM)


# Обработчик описания проблемы
@router.message(Consult.DESCRIBE_PROBLEM)
async def describe_problem(message: Message, state: FSMContext):
    await state.update_data(problem_description=message.text)
    # Инлайн клавиатура для загрузки файлов
    file_upload_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Далее", callback_data="go_confirm_query")],
        [InlineKeyboardButton(text='Отмена', callback_data='cancel_order')],
    ])

    await message.answer("Загрузите файлы, если нужно, или нажмите 'Далее'.", reply_markup=file_upload_kb)
    await state.set_state(Consult.UPLOAD_FILES)


@router.message(Consult.UPLOAD_FILES)
async def process_file_to_lawyer(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    files = data.get('files', [])
    kb = InlineKeyboardBuilder()
    kb.button(text='Далее', callback_data='go_confirm_query')
    kb.button(text='Отмена', callback_data='cancel_order')

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

    await state.update_data(files=files)

    await bot.send_message(chat_id=message.from_user.id,
                           text="Файл успешно загружен. Загрузите следующий или нажмите 'Далее'.",
                           reply_markup=kb.as_markup())


#Обработчик подтверждения заказа
@router.callback_query(F.data == "go_confirm_query", UserFilter())
async def process_next(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = call.from_user.id
    topic = data.get("topic")
    problem_description = data.get("problem_description")
    files = data.get("files", [])
    order_id = str(uuid.uuid4())

    if not topic or not problem_description:
        await call.message.answer("Некорректные данные заказа. Попробуйте снова.")
        return

    # Установка статуса заказа
    order_status = "active"

    # Создание заказа в базе данных
    await add_order(order_id,
                    user_id,
                    problem_description,
                    order_status,
                    topic,
                    files)

    if topic == "legal_audit":
        # Отправка администраторам
        admins = await get_admins()
        for admin_id in admins:
            try:
                await call.message.bot.send_message(
                    admin_id,
                    f"Новый заказ на юридический аудит:\n\n"
                    f"ID заказа: {order_id}\n"
                    f"Имя пользователя: {call.from_user.full_name}\n"
                    f"ID пользователя: {user_id}\n"
                    f"Описание: {problem_description}"
                    )
                # Пересылка файлов
                for file_id in files:
                    try:
                        if file_id.startswith("photo_"):  # Или используйте другой метод для определения типа
                            await call.bot.send_photo(lawyers_group, file_id)
                        else:
                            await call.bot.send_document(lawyers_group, file_id)
                    except Exception as e:
                        print(f"Ошибка при отправке файла: {e}")
            except Exception as e:
                print(f"Ошибка при отправке сообщения администратору {admin_id}: {e}")
        await state.clear()
    else:
        accept_order_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Принять заказ", callback_data=f"accept_{order_id}")]
        ])
        try:
            await call.message.bot.send_message(
                lawyers_group,
                f"Новый заказ:\n\n"
                f"ID заказа: {order_id}\n"
                f"Описание: {problem_description}",
                reply_markup=accept_order_kb
                )
            # Пересылка файлов
            for file_id in files:
                try:
                    file_info = await call.message.bot.get_file(file_id)
                    file_extension = file_info.file_path.split('.')[-1].lower()
                    # Check if it's a photo based on the file extension or MIME type
                    if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
                        await call.bot.send_photo(lawyers_group, file_id)
                    else:
                        await call.bot.send_document(lawyers_group, file_id)
                except Exception as e:
                    print(f"Ошибка при отправке файла: {e}")
        except Exception as e:
            print(f"Ошибка при отправке сообщения в группу юристов: {e, lawyers_group}")
        await state.clear()


@router.message(F.text=="Мои заказы", UserFilter())
async def send_active_orders(call: CallbackQuery, bot: Bot):
    """
    Проверяет на наличие заказов, если таковых нет, создает
    """
    order_id = await get_active_order(call.from_user.id)
    lawyer_id = await get_active_order_lawyer_id(call.from_user.id, order_id)
    if order_id:
        if not lawyer_id:
            """
            Если исполнитель по существующему заказу не выбран
            """
            await bot.send_message(chat_id=call.from_user.id,
                                   text='Вы еще не выбрали исполнителя по заказу.')
        else:
            """
            Вывод информации по текущему заказу
            """
            order_info = get_order_info_by_order_id(order_id)
            await bot.send_message(chat_id=call.from_user.id,
                                   text=f'У вас уже имеется действующий заказ:\n{order_info}')
    else:
        await call.answer("У вас нет активных заказов")


"""
ВЕТКА ОТКЛИКА НА ЗАКАЗ
"""

@router.callback_query(F.data.startswith("accept_"))
async def lawyer_accept_order(callback: CallbackQuery, state: FSMContext):
    order_id = callback.data.split("_")[1]
    await state.update_data(order_id=order_id, lawyer_id=callback.from_user.id)

    await callback.message.bot.send_message(
        chat_id=callback.from_user.id,
        text="Укажите стоимость ваших услуг. Учтите, что будет вычтена комиссия сервиса."
    )
    await state.set_state(LawyerResponse.ENTER_PRICE)


@router.callback_query(F.data == "edit_response")
async def lawyer_re_accept_order(callback: CallbackQuery, state: FSMContext):
    order_id = callback.data.split("_")[1]
    await state.update_data(order_id=order_id, lawyer_id=callback.from_user.id)

    await callback.message.bot.send_message(
        chat_id=callback.from_user.id,
        text="Укажите стоимость ваших услуг. Учтите, что будет вычтена комиссия сервиса."
    )
    await state.set_state(LawyerResponse.ENTER_PRICE)


@router.message(LawyerResponse.ENTER_PRICE)
async def enter_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        if price <= 0:
            raise ValueError("Стоимость должна быть положительным числом.")

        await state.update_data(price=price)
        await message.answer("Теперь укажите примерный срок исполнения заказа в днях.")
        await state.set_state(LawyerResponse.ENTER_DEADLINE)
    except ValueError as e:
        await message.answer(f"Ошибка: {str(e)}. Укажите корректную стоимость.")


@router.message(LawyerResponse.ENTER_DEADLINE)
async def enter_deadline(message: Message, state: FSMContext):
    try:
        days = int(message.text)
        if days <= 0:
            raise ValueError("Срок должен быть положительным числом.")

        await state.update_data(deadline=days)
        data = await state.get_data()

        await message.answer(
            f"Проверьте введенные данные:\n\n"
            f"Стоимость услуг: {data['price']} ₽ \n"
            f"Срок исполнения: {data['deadline']} дней.\n\n"
            f"Верно?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Откликнуться", callback_data="confirm_response")],
                [InlineKeyboardButton(text="Исправить", callback_data="edit_response")]
            ])
        )
    except ValueError as e:
        await message.answer(f"Ошибка: {str(e)}. Укажите корректный срок в днях.")


@router.callback_query(F.data == "confirm_response")
async def confirm_response(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_info = await get_order_info_by_order_id(data["order_id"])  # Функция для получения ID пользователя, создавшего заказ
    user_id = order_info[0]
    try:
        await callback.message.bot.send_message(
            chat_id=user_id,
            text=(
                f"На ваш заказ откликнулся юрист:\n\n"
                f"ФИО: {callback.from_user.full_name}\n"
                f"Стоимость услуг: {data['price']} ₽ \n"
                f"Срок исполнения: {data['deadline']} дней.\n\n"
                f"Если вы согласны, нажмите 'Выбрать исполнителя'."
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Выбрать исполнителя",
                                      callback_data=f"choose_{data.get('order_id')}_{callback.from_user.id}_{data['price']}_{data['deadline']}")]
            ])
        )
        await callback.message.answer("Ваш отклик отправлен пользователю.")
        await state.clear()
    except Exception as e:
        await callback.message.answer(f"Ошибка при отправке отклика: {e}")


@router.callback_query(F.data.startswith("choose_"))
async def choose_lawyer(callback: CallbackQuery, state: FSMContext):
    _, order_id, lawyer_id, price, deadline = callback.data.split("_")
    await state.update_data(
        order_id=order_id,
        lawyer_id=lawyer_id,
        price=price,
        deadline=deadline
    )

    # Проверяем статус заказа и обновляем информацию о юристе
    order_info = await get_order_info_by_order_id(order_id)
    if not order_info or order_info[1] == "in_progress":  # Если заказ уже взят юристом
        await callback.message.answer("Этот заказ уже был передан другому юристу.")
        return
    offer_contract_path = "offer_contract.pdf"
    # Получаем user_id клиента из информации о заказе
    user_id = order_info[0]

    # Отправка PDF-файла с договором оферты
    try:
        # Открываем файл и передаем его как объект в InputFile
        with open(offer_contract_path, "rb") as file:
            offer_contract = InputFile(file, filename="offer_contract.pdf")  # Оборачиваем файл в InputFile

            await callback.bot.send_document(
                chat_id=user_id,
                document=offer_contract,
                caption="Пожалуйста, ознакомьтесь с договором оферты перед оплатой.",
            )

        # Переход к следующему этапу
        await state.update_data(order_id=order_id, lawyer_id=lawyer_id)
        await callback.bot.send_message(
            chat_id=user_id,
            text="После ознакомления с договором оферты, пожалуйста, перейдите к оплате.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Оплатить", callback_data=f"pay_{order_id}")]
            ])
        )
        await state.set_state(PaymentResponse.AWAITING_PAYMENT)

    except Exception as e:
        logger.error(f"Ошибка при отправке договора оферты: {e, os.path.exists(offer_contract_path)}")
        await callback.message.answer("Произошла ошибка при отправке договора. Попробуйте снова.")


@router.callback_query(F.data.startswith("pay_"))
async def check_payment(callback: CallbackQuery, state: FSMContext):
    order_id = callback.data.split("_")[1]

    # Проверка состояния
    data = await state.get_data()
    if data.get("order_id") != order_id:
        await callback.message.answer("Произошла ошибка при обработке заказа. Попробуйте снова.")
        return

    # Заглушка для проверки оплаты
    """
    В будущем здесь будет код, связанный с интеграцией с платежной системой.
    """
    payment_successful = True  # Эмуляция успешной оплаты

    if payment_successful:
        # Регистрация заказа в БД
        try:
            order_day_start = datetime.today().date()
            order_day_end = datetime.today().date() + timedelta(days=int(data.get("deadline")))

            added_to_db = await add_order_info(
                order_id=order_id,
                order_cost=data.get("price"),
                order_day_start=order_day_start,
                order_day_end=order_day_end,
                order_status="in_progress"
            )

            if added_to_db:
                await callback.message.answer("Оплата успешно подтверждена! Ваш заказ зарегистрирован.")
                await callback.bot.send_message(
                    chat_id=data.get("lawyer_id"),
                    text=f"Пользователь подтвердил оплату. Начинайте выполнение заказа (ID заказа: {order_id}).",
                )
                # Сброс состояния
                await state.clear()
            else:
                await callback.message.answer("Произошла ошибка при регистрации заказа. Обратитесь в поддержку.")
        except Exception as e:
            logger.error(f"Ошибка при регистрации заказа: {e}")
            await callback.message.answer("Произошла ошибка при обработке заказа. Обратитесь в поддержку.")
    else:
        await callback.message.answer("Оплата не была подтверждена. Попробуйте снова или обратитесь в поддержку.")

"""
ВЕТКА ПЕРЕПИСОК
"""

@router.message(F.text == "Диалог")
async def handle_dialog_button(message: Message, state: FSMContext):
    user_id = message.from_user.id

    # Проверка наличия активного заказа и собеседника
    order_data = await get_active_order_and_partner(user_id)
    if order_data == ():
        await message.answer("Для начала диалога нужен активный заказ.")
        return

    order_id, partner_id = order_data

    current_state = await state.get_state()

    if current_state == DialogState.active.state:
        # Завершение диалога
        await state.clear()
        await message.answer("Диалог завершен.")
        # Уведомляем второго пользователя
        await message.bot.send_message(partner_id, "Ваш собеседник завершил диалог.")
    else:
        # Начало диалога
        await state.set_state(DialogState.active)
        await state.update_data(partner_id=partner_id, order_id=order_id)
        await message.answer("Диалог начат. Вы можете отправлять сообщения.")
        # Уведомляем второго пользователя
        await message.bot.send_message(partner_id, "Ваш собеседник начал диалог.")


@router.message()
async def on_message_in_dialog(message: Message, state: FSMContext):
    user_id = message.from_user.id

    # Проверка участия в активном диалоге
    current_state = await state.get_state()
    if current_state == DialogState.active.state:
        data = await state.get_data()
        partner_id = data.get("partner_id")
        order_id = data.get("order_id")

        text = message.text
        file_id = None
        file_type = None

        # Если сообщение содержит файл
        if message.document:
            file_id = message.document.file_id
            file_type = "document"
        elif message.photo:
            file_id = message.photo[-1].file_id  # Берем последнюю (самую качественную) фотографию
            file_type = "photo"

        # Отправляем сообщение собеседнику
        if text or file_id:
            await message.bot.send_message(partner_id, text or "Отправлен файл")
            if file_id:
                if file_type == "document":
                    await message.bot.send_document(partner_id, file_id)
                elif file_type == "photo":
                    await message.bot.send_photo(partner_id, file_id)

            # Сохраняем сообщение в базе данных
            await save_message(order_id, sender_id=user_id, receiver_id=partner_id, message_text=text, file_id=file_id, file_type=file_type)
    else:
        await message.answer("Вы не участвуете в диалоге. Для начала нажмите 'Диалог'.")
