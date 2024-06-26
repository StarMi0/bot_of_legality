from aiogram.filters.callback_data import CallbackData


class BranchChoose(CallbackData, prefix='branch'):
    branch: str


class GetResponse(CallbackData, prefix='response'):
    uniq_id: str
    user_id: int

class GetAnswer(CallbackData, prefix='response'):
    order_id: str
    user_id: int


class GoToDevelopTime(CallbackData, prefix='go_to_develop_time'):
    order_id: str
    original_user_id: int


class ConfirmOrDeleteOffer(CallbackData, prefix='confirmation'):
    offer_id: str
    lawyer_id: str
    confirm: bool





