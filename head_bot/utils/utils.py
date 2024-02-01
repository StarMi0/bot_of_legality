import uuid

from database.request import get_user_role


async def generate_unique_identifier():
    unique_id = str(uuid.uuid4().hex)
    return unique_id

# Функция для проверки регистрации пользователя
async def check_registration(user_id: int)-> bool:
    role = await get_user_role(user_id)
    print(role)
    # Здесь должна быть реализована логика проверки регистрации пользователя
    # Возвращает роль пользователя, если пользователь зарегистрирован, и False, если нет
    return role if role else False


async def check_active_query(user_id):
    # Проверка есть ли активные вопросы у пользователя
    # возвращает True если есть, False если нет
    return False