from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.callbackdata import BranchChoose

select_service = InlineKeyboardBuilder()
select_service.button(text="Юридическая консультация", callback_data=BranchChoose(branch="consult_group_id"))
select_service.button(text="Автоюрист", callback_data=BranchChoose(branch="auto_consult_id"))
select_service.button(text="Юридический аудит",  callback_data=BranchChoose(branch="audit_id"))
select_service.button(text="Общие вопросы",  callback_data=BranchChoose(branch="all_consult_id"))
select_service.adjust(1)
select_service_kb = select_service.as_markup()




