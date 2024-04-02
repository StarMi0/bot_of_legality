from aiogram.filters import Command, StateFilter
from aiogram import F
from handlers.lawyers import router_lawyers, process_response, get_develop_time, get_develop_price, \
    send_offer_to_client, confirm_develop_time, go_to_develop_time_lawyer
from utils.callbackdata import BranchChoose, GetResponse, ConfirmOrDeleteOffer, GoToDevelopTime
from utils.isadmin import IsAdmin
from handlers.users import router_users, get_start, process_input_file, clear_state, process_file_from_user, \
    send_query_to_lawyers, process_branch, confirm_or_delete_offer, send_select_service, send_active_orders, \
    process_file_to_lawyer, send_query_to_confirm
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
    router_users.callback_query.register(send_active_orders, F.data == "get_active_orders")

    """Question to lawyer"""
    router_users.message.register(process_file_from_user, F.text, StateFilter(Consult.question))
    router_users.message.register(process_file_to_lawyer, F.document, StateFilter(Consult.additional_files))
async def register_lawyers():
    router_lawyers.callback_query.register(process_response, GetResponse.filter())
    router_lawyers.message.register(get_develop_time, F.text, StateFilter(Consult.develop_time))
    router_lawyers.message.register(get_develop_price, F.text, StateFilter(Consult.price))
    router_lawyers.callback_query.register(go_to_develop_time_lawyer, GoToDevelopTime.filter())
    router_lawyers.callback_query.register(confirm_develop_time, F.data == 'go_to_price_lawyer')
    router_lawyers.callback_query.register(send_offer_to_client, F.data == 'send_offer_to_client')
