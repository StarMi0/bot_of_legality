import uuid

async def generate_unique_identifier():
    unique_id = str(uuid.uuid4().hex)
    return unique_id

# Функция для проверки регистрации пользователя
async def check_registration(user_id: str)-> bool:
    # Здесь должна быть реализована логика проверки регистрации пользователя
    # Возвращает True, если пользователь зарегистрирован, и False, если нет
    return True


