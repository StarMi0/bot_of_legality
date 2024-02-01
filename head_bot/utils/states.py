from aiogram.fsm.state import StatesGroup, State


class Consult(StatesGroup):
    question = State()
    question_to = State()
    additional_files = State()
    file_add = State()
    price = State()
    develop_time = State()

# class OrderInfoLawyer(StatesGroup):
