
from aiogram.filters.callback_data import CallbackData



class BranchChoose(CallbackData, prefix='branch'):
    branch: str


class GetResponse(CallbackData, prefix='response'):
    uniq_id: str
    user_id: int


class ConfirmOrDeleteOffer(CallbackData, prefix='confirmation'):
    order_id: str
    user_id: int
    lawyer_id: int
    confirm: bool
