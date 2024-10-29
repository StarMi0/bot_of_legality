from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from main import dp


async def get_state_user(user_id: int, reset: bool = False,
                         clear_data=False):
    state = dp.fsm.get_context(user_id, user_id)
    if reset:
        await state.reset_state(with_data=clear_data)

    return state


async def save_data_state(chat_id: int, **kwargs):
    """Сохранение данных в state"""
    state = await get_state_user(chat_id)
    await state.update_data(**kwargs)


async def get_data_from_state(chat_id: int, key, default_value=None):
    """Возвращает данные из state"""
    state = await get_state_user(chat_id)
    return (await state.get_data()).get(key, default_value)


async def set_state(chat_id: int,  state: str):
    """Устанавливает состояние"""
    current_state = await get_state_user(chat_id)
    await current_state.set_state(state)
