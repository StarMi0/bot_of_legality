from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    fio = State()
    date_birth = State()
    education = State()
    upload_documents = State()
    data_to_admin = State()

class SupportStates(StatesGroup):
    waiting_for_problem_description = State()

class Consult(StatesGroup):
    CHOOSE_TOPIC = State()
    DESCRIBE_PROBLEM = State()
    UPLOAD_FILES = State()

class LawyerResponse(StatesGroup):
    ENTER_PRICE = State()
    ENTER_DEADLINE = State()

class PaymentResponse(StatesGroup):
    CONFIRM_RESPONSE = State()
    AWAITING_PAYMENT = State()

# Определяем состояние для диалога
class DialogState(StatesGroup):
    active = State()  # Состояние активного диалога
    partner_id = State()  # ID собеседника

class EndOrder(StatesGroup):
    SEND_FINAL_TEXT = State()
    SEND_FINAL_FILES = State()
    SAVE_FINAL_FILES = State()

