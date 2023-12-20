from typing import List
import aiomysql
from utils.config import db_config

async def create_pool():
    return await aiomysql.create_pool(**db_config)

# Айди юзера и админа хранится в числовом виде в базе
async def user_exists(user_id: int):
    try:
        pool = await create_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                query = "SELECT * FROM users WHERE user_id = %s"
                await cursor.execute(query, (user_id,))
                result = await cursor.fetchone()

                return result is not None
    except Exception as e:
        print(f"Error checking if user exists: {e}")
        return False

# Понять в каком виде хранится дата, дописать тайпинг
# Айди юзера и админа хранится в числовом виде в базе
async def add_user(user_id: int, role: str, registration_data):
    try:
        pool = await create_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                query = "INSERT INTO users (user_id, role, registration_data) VALUES (%s, %s, %s)"
                await cursor.execute(query, (user_id, role, registration_data))

            await connection.commit()
    except Exception as e:
        print(f"Error adding user: {e}")


# Добавить в базу данных таблицу админов
async def get_admins() -> List[int]:
    try:
        pool = await create_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                query = "SELECT admin_id FROM admin"
                await cursor.execute(query,)
                result = cursor.fetchall()
            return result
    except Exception as e:
        print(f"Error adding user: {e}")


