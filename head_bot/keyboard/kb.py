from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.callbackdata import BranchChoose

select_service = InlineKeyboardBuilder()
select_service.button(text="Юридическая консультация", callback_data=BranchChoose(branch="consult_group_id"))
select_service.button(text="Автоюрист", callback_data=BranchChoose(branch="auto_consult_id"))
select_service.button(text="Юридический аудит", callback_data=BranchChoose(branch="audit_id"))
select_service.button(text="Общие вопросы", callback_data=BranchChoose(branch="all_consult_id"))
select_service.adjust(1)
select_service_kb = select_service.as_markup()


async def get_main_user_kb():
    main_kb = InlineKeyboardBuilder()
    main_kb.button(text="Заказать услугу", callback_data='get_select_service')
    main_kb.button(text="Отправить сообщение исполнителю", callback_data='get_active_orders')
    main_kb.adjust(1)
    return main_kb.as_markup()


async def get_main_lawyer_kb():
    main_kb = InlineKeyboardBuilder()
    main_kb.button(text="Мои заказы", callback_data='get_active_orders_lawyer')
    # main_kb.button(text="Отправить сообщение исполнителю", callback_data='get_active_orders')
    main_kb.adjust(1)
    return main_kb.as_markup()


async def get_main_admin_kb():
    main_kb = InlineKeyboardBuilder()
    main_kb.button(text="Мои заказы", callback_data='get_active_orders')
    # main_kb.button(text="Отправить сообщение исполнителю", callback_data='get_active_orders')
    main_kb.adjust(1)
    return main_kb.as_markup()
