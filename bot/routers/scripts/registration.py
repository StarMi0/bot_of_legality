from aiogram import Router, types, Bot, F
from aiogram.filters import Command, BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from routers.states import Registration
from routers.users.admin import AdminFilter
from database.request import add_user, add_document, add_lawyer_info, user_exist, get_admins
from database.redis_db import get_temp_user_data, set_temp_user_data, delete_temp_user_data
from utils.config import invite_link


router = Router(name=__name__)


class IsNotUserRegisteredFilter(BaseFilter):
    """Фильтр для проверки, что пользователь не зарегистрирован."""
    async def __call__(self, message: Message) -> bool:
        return not await user_exist(message.from_user.id)


@router.message(Command("start"), IsNotUserRegisteredFilter())
async def unregistered_start_router(message: types.Message):
    """
    Роутер для незарегистрированных пользователей для начала регистрации, реагирующий на /start
    """
    text = ('Вы не зарегистрированы.\n'
            'Для начала работы с ботом вам нужно пройти регистрацию. \n'
            'Выберите свою роль:')

    # Создаем клавиатуру
    kb = InlineKeyboardBuilder()
    kb.button(text='Пользователь', callback_data='registration_user')
    kb.button(text='Юрист', callback_data='registration_lawyer')
    kb.adjust(1)
    await message.reply(text=text, reply_markup=kb.as_markup())


@router.callback_query(F.data.in_({"registration_user", "registration_lawyer"}))
async def process_role(call: CallbackQuery, bot: Bot, state: FSMContext):
    """
    Обработчик выбора роли при регистрации.
    """
    await call.answer()
    if call.data == 'registration_user':
        await state.update_data(ROLE='user')
    else:
        await state.update_data(ROLE='lawyer')
    text = 'Введите свое ФИО одной строкой через пробел:\n например: Иванов Иван Иванович'
    kb = InlineKeyboardBuilder()
    kb.button(text='Назад', callback_data='back_choose_role')
    await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=kb.as_markup())
    await state.set_state(Registration.fio)


@router.message(Registration.fio)
@router.callback_query(F.data.in_({"registration_user", "registration_lawyer"}))
async def process_fio(message: types.Message | CallbackQuery, bot: Bot, state: FSMContext):
    """
    Обработчик для ввода ФИО.
    """
    if isinstance(message, types.Message):
        await state.update_data(FIO=message.text)
    else:
        await message.answer()

    # Получаем данные из состояния для проверки роли
    text = f'{message.text}\nВведите свою дату рождения в формате: дд.мм.гггг:\n например: 11.11.2011'
    kb = InlineKeyboardBuilder()
    data = await state.get_data()
    if data.get('ROLE') == 'user':
        kb.button(text='Назад', callback_data='registration_user')
    else:
        kb.button(text='Назад', callback_data='registration_lawyer')

    # Отправляем сообщение с клавиатурой
    await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=kb.as_markup())
    await state.set_state(Registration.date_birth)


@router.message(Registration.date_birth)
@router.callback_query(F.data.in_({"registration_user", "registration_lawyer"}))
async def process_date_birth(message: types.Message | CallbackQuery, bot: Bot, state: FSMContext):
    """
    Обработчик для даты рождения
    """
    if isinstance(message, types.Message):
        await state.update_data(DATE=message.text)
    else:
        await message.answer()
    data = await state.get_data()

    # Получаем данные из состояния для проверки роли
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
        await state.set_state(Registration.education)


@router.callback_query(F.data == "end_reg_user")
async def end_user_registration(call: CallbackQuery, state: FSMContext):
    """
    Завершение регистрации для пользователя.
    """
    await call.answer()
    data = await state.get_data()
    user_fio = data.get("FIO")
    user_date_birth = data.get("DATE")
    await add_user(user_id=str(call.from_user.id), user_name=call.from_user.username,
                   user_fio=user_fio, user_date_birth=user_date_birth, role='user')
    text = 'Регистрация завершена! Вы можете пользоваться ботом.'
    await call.message.edit_text(text=text)
    await state.clear()


@router.message(Registration.education)
@router.callback_query(F.data.in_({"registration_user", "registration_lawyer"}))
async def process_education(message: types.Message | CallbackQuery, bot: Bot, state: FSMContext):
    """
    Обработчик образования юриста
    """
    if isinstance(message, types.Message):
        await state.update_data(EDUCATION=message.text)
    else:
        await message.answer()
    text = f'{message.text}\n'
    kb = InlineKeyboardBuilder()
    kb.button(text='Назад', callback_data='registration_date_birth')
    kb.button(text='Далее', callback_data='add_documents')

    await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=kb.as_markup())


@router.callback_query(F.data == "add_documents")
async def upload_documents(call: CallbackQuery, bot: Bot, state: FSMContext):
    """
    Состояние для загрузки документов
    """
    text = (
        "Вы можете загрузить свои документы (дипломы, сертификаты и т.д.).\n"
        "После загрузки всех документов нажмите 'Далее'."
    )
    kb = InlineKeyboardBuilder()
    kb.button(text='Далее', callback_data='save_documents')

    await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=kb.as_markup())
    await state.set_state(Registration.upload_documents)


@router.message(Registration.upload_documents)
async def handle_document_upload(message: types.Message, state: FSMContext):
    """
    Обработка загрузки документа
    """
    user_data = await state.get_data()
    documents = user_data.get("DOCUMENTS", [])

    if message.document:
        documents.append(message.document.file_id)
    elif message.photo:
        # Сохраняем файл самого крупного фото
        documents.append(message.photo[-1].file_id)
    elif message.text:
        # Если это текст, сохраняем его как строку
        documents.append(message.text)
    else:
        # Если сообщение другого типа, можно игнорировать или сохранить, как требуется
        await message.reply("Этот тип сообщения не поддерживается для загрузки.")
        return

    await state.update_data(DOCUMENTS=documents)
    kb = InlineKeyboardBuilder()
    kb.button(text='Далее', callback_data='save_documents')
    await message.reply("Документ успешно загружен. Загрузите следующий или нажмите 'Далее'.", reply_markup=kb.as_markup())


@router.callback_query(F.data == "save_documents", AdminFilter())
async def save_documents(call: CallbackQuery, state: FSMContext):
    """
    Сохранение загруженных документов и переход к следующему шагу
    """
    user_data = await state.get_data()
    documents = user_data.get("DOCUMENTS", [])

    if not documents:
        await call.answer("Вы не загрузили ни одного документа.", show_alert=True)
        return

    # Сохранение документов в базу данных или другой обработчик
    # Здесь можно добавить код для сохранения документов

    await call.message.answer("Ваши документы успешно сохранены.")
    # Переход к следующему шагу
    await state.set_state(Registration.data_to_admin)

    # Сбор информации для администраторов
    user_fio = user_data.get("FIO")
    user_date_birth = user_data.get("DATE")
    education = user_data.get("EDUCATION")
    documents = user_data.get("DOCUMENTS")

    # Формируем текст для администраторов
    admin_text = (
        f"<b>Новая заявка на регистрацию юриста</b>\n\n"
        f"ФИО: {user_fio}\n"
        f"Дата рождения: {user_date_birth}\n"
        f"Образование: {education}\n\n"
        f"Пользователь: @{call.from_user.username}"
    )

    # Создаем кнопки для подтверждения или отказа в регистрации
    kb = InlineKeyboardBuilder()
    kb.button(text="Подтвердить регистрацию", callback_data="confirm_registration")
    kb.button(text="Отказать в регистрации", callback_data="reject_registration")
    kb.adjust(1)

    # Отправляем сообщение администраторам
    await call.message.reply(admin_text, parse_mode="HTML", reply_markup=kb.as_markup())

    # Обработка и отправка документов и фотографий администраторам
    for file_id in documents:
        try:
            # Сначала пытаемся отправить как документ
            await call.message.reply_document(file_id)
        except Exception:
            # Если не удалось, отправляем как фото
            try:
                await call.message.reply_photo(file_id)
            except Exception as e:
                # Если ни документ, ни фото, логируем ошибку (опционально)
                await call.message.reply(f"Не удалось отправить файл с ID: {file_id}. Ошибка: {e}")

@router.callback_query(F.data == "confirm_registration")
async def confirm_registration(call: CallbackQuery, bot: Bot, state: FSMContext):
    """
    Обработка подтверждения регистрации пользователя.
    """
    user_data = await state.get_data()
    lawyer_id = call.from_user.id
    lawyer_data = {
        "username": call.from_user.username,
        "FIO": user_data.get("FIO"),
        "DATE": user_data.get("DATE"),
        "EDUCATION": user_data.get("EDUCATION")
    }

    # Добавление пользователя в базу данных
    await add_user(user_id=lawyer_id, user_name=lawyer_data["username"],
                   user_fio=lawyer_data["FIO"], user_date_birth=lawyer_data["DATE"], role='lawyer')
    await add_lawyer_info(user_id=lawyer_id, education=lawyer_data["EDUCATION"])

    # Приглашение в группу
    await bot.send_message(lawyer_id, f"Поздравляем! Ваша регистрация подтверждена. Присоединяйтесь к нашей группе: {invite_link}")

    # Сообщение об успешной регистрации
    await call.message.answer("Вы успешно зарегистрированы!")

    # Закрытие состояний
    await state.clear()


@router.callback_query(F.data == "reject_registration")
async def reject_registration(call: CallbackQuery, bot: Bot, state: FSMContext):
    """
    Обработка отказа в регистрации пользователя.
    """
    user_data = await state.get_data()
    lawyer_id = call.from_user.id

    # Уведомление пользователя об отказе
    await bot.send_message(lawyer_id, "В регистрации отказано. Ваши данные не будут сохранены.")

    # Закрытие состояний
    await state.clear()

    # Отправка сообщения администраторам
    await call.message.answer("Заявка на регистрацию отклонена.")


@router.message(IsNotUserRegisteredFilter(), ~F.state)
async def handle_any_message(message: types.Message):
    """
    Обработчик для незарегистрированных пользователей, реагирующий на любое сообщение.
    """
    text = 'Вы не зарегистрированы.\nДля начала работы с ботом вам нужно пройти регистрацию. \nВыберите свою роль:'

    # Создаем клавиатуру
    kb = InlineKeyboardBuilder()
    kb.button(text='Пользователь', callback_data='registration_user')
    kb.button(text='Юрист', callback_data='registration_lawyer')
    kb.adjust(1)
    await message.reply(text=text, reply_markup=kb.as_markup())