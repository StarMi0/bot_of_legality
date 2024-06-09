from aiogram.fsm.state import StatesGroup, State


class Consult(StatesGroup):
    question = State()
    question_to = State()
    additional_files = State()
    file_add = State()
    price = State()
    develop_time = State()

    fio = State()
    date_birth = State()
    education = State()
    education_documents = State()
    lawyer_client_chat = State()
    get_end_info = State()
# class OrderInfoLawyer(StatesGroup):
