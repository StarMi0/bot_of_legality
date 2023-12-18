from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


select_service = InlineKeyboardBuilder()
select_service.button(text="Юридическая консультация", callback_data="Legality_consult")
select_service.button(text="Автоюрист", callback_data="Auto_consult")
select_service.button(text="Юридический аудит", callback_data="Audit")
select_service.button(text="Общие вопросы", callback_data="All_consult")
select_service.adjust(1)
select_service_kb = select_service.as_markup()




