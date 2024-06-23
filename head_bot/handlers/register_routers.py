from aiogram.filters import Command, StateFilter
from aiogram import F
from handlers.lawyers import router_lawyers, process_response, get_develop_time, get_develop_price, \
    send_offer_to_client, confirm_develop_time, go_to_develop_time_lawyer, send_main_lawyer_kb, \
    on_lawyer_client_chat_start, get_active_orders_lawyer, send_order_info, on_end_order, after_confirm_close, \
    on_get_end_info, on_full_end
from handlers.registration import process_role, process_fio, process_date_birth, process_education, process_documents, \
    choose_role, add_lawyer_to_db
from utils.callbackdata import BranchChoose, GetResponse, ConfirmOrDeleteOffer, GoToDevelopTime
from utils.dialogfilter import DialogFilter
from utils.isadmin import IsAdmin
from handlers.users import router_users, get_start, process_input_file, clear_state, process_file_from_user, \
    send_query_to_lawyers, process_branch, confirm_or_delete_offer, send_select_service, send_active_orders, \
    process_file_to_lawyer, send_query_to_confirm, registration_end_user, registration_end_lawyer, process_dialog, \
    end_chat, on_client_confirm_end, on_client_dispute_end, on_send_dispute_to_admins, on_cancel_order, \
    on_get_dispute_text
from aiogram.filters import CommandStart, StateFilter
from utils.states import Consult


async def register_users():
    router_users.message.register(get_start, CommandStart())
    router_users.callback_query.register(process_branch, BranchChoose.filter())
    router_users.message.register(process_input_file, F.text, StateFilter(Consult.question))
    router_users.callback_query.register(clear_state, F.data == "state_clear")
    router_users.message.register(process_file_from_user, F.document, StateFilter(Consult.file_add))
    router_users.callback_query.register(send_query_to_lawyers, F.data == 'send_query_to_lawyers_chat')
    router_users.callback_query.register(send_query_to_confirm, F.data == 'go_confirm_query')
    router_users.callback_query.register(confirm_or_delete_offer, ConfirmOrDeleteOffer.filter())

    """Main kb"""
    router_users.callback_query.register(send_select_service, F.data == "get_select_service")
    router_users.callback_query.register(on_lawyer_client_chat_start,  F.data.startswith("get_active_orders_"))
    router_users.callback_query.register(get_active_orders_lawyer, F.data == "get_active_orders_lawyer")

    """Question to lawyer"""
    router_users.message.register(process_file_from_user, F.text, StateFilter(Consult.question))
    router_users.message.register(process_file_to_lawyer, F.document, StateFilter(Consult.additional_files))
    """REGISTRATION"""

    router_users.callback_query.register(process_role, F.data.startswith('registration'))
    router_users.callback_query.register(process_fio, F.data == 'registration_process_fio')
    router_users.callback_query.register(process_date_birth, F.data == 'registration_date_birth')
    router_users.callback_query.register(registration_end_user, F.data == 'end_reg_user')
    router_users.callback_query.register(registration_end_lawyer, F.data == 'end_reg_lawyer')
    router_users.callback_query.register(choose_role, F.data == 'back_choose_role')
    router_users.callback_query.register(add_lawyer_to_db, F.data == 'add_lawyer_to_db')
    router_users.message.register(process_fio, StateFilter(Consult.fio))
    router_users.message.register(process_date_birth, StateFilter(Consult.date_birth))
    router_users.message.register(process_education, StateFilter(Consult.education))
    router_users.message.register(process_documents, F.document, StateFilter(Consult.education_documents))
    router_users.message.register(process_dialog, StateFilter(Consult.client_lawyer_chat))

    router_lawyers.callback_query.register(on_cancel_order, F.data.startswith('order_cancel_'))
    router_lawyers.callback_query.register(on_client_confirm_end, F.data.startswith('user_confirm_end_'))
    router_lawyers.callback_query.register(on_client_dispute_end, F.data.startswith('user_dispute_end_'))
    router_lawyers.callback_query.register(on_send_dispute_to_admins, F.data.startswith('send_dispute'))
    router_lawyers.message.register(on_get_dispute_text, StateFilter(Consult.dispute_info))


async def register_lawyers():
    router_lawyers.callback_query.register(process_response, GetResponse.filter())
    router_lawyers.message.register(get_develop_time, F.text, StateFilter(Consult.develop_time))
    router_lawyers.message.register(get_develop_price, F.text, StateFilter(Consult.price))
    router_lawyers.callback_query.register(go_to_develop_time_lawyer, GoToDevelopTime.filter())
    router_lawyers.callback_query.register(confirm_develop_time, F.data == 'go_to_price_lawyer')
    router_lawyers.callback_query.register(send_offer_to_client, F.data == 'send_offer_to_client')
    router_lawyers.callback_query.register(send_main_lawyer_kb, F.data == 'main_lawyer')
    router_lawyers.callback_query.register(on_lawyer_client_chat_start, F.data.startswith('question_lawyer_'))
    router_lawyers.callback_query.register(on_end_order, F.data.startswith('close_order_'))
    router_lawyers.callback_query.register(after_confirm_close, F.data.startswith('confirm_close_'))
    router_lawyers.callback_query.register(on_full_end, F.data.startswith('full_close_'))
    router_lawyers.message.register(on_get_end_info, StateFilter(Consult.get_end_info))
    router_lawyers.callback_query.register(send_order_info, F.data.startswith('order_'))

    router_lawyers.message.register(end_chat, F.text == 'Закончить чат', DialogFilter())
    router_lawyers.message.register(process_dialog, DialogFilter())
    # router_lawyers.message.register(process_dialog)

    """admin"""
    router_lawyers.callback_query.register(on_client_confirm_end, F.data.startswith('admin_end_'))
