import uuid

from database.request import get_user_role, get_active_order


async def generate_unique_identifier():
    unique_id = str(uuid.uuid4().hex)
    return unique_id


# Функция для проверки регистрации пользователя
async def check_registration(user_id: str) -> bool:
    role = await get_user_role(user_id)
    print(role)
    # Здесь должна быть реализована логика проверки регистрации пользователя
    # Возвращает роль пользователя, если пользователь зарегистрирован, и False, если нет
    return role if role else False


async def check_active_query(user_id):
    # Проверка есть ли активные вопросы у пользователя
    # возвращает True если есть, False если нет
    return await get_active_order(user_id)


from datetime import datetime, timedelta


def get_expired_time():
    future_time = datetime.now() + timedelta(minutes=15)
    return future_time.strftime('%Y-%m-%dT%H:%M:%S')


