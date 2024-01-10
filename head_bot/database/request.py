import os
from typing import List

import aiomysql

my_host = os.getenv('MYSQL_HOST', 'localhost')
my_user = os.getenv('MYSQL_USER', 'admin')
my_password = os.getenv('DB_ROOT_PASSWORD', 'Qwerty123456')
my_database = "legality"


# Функция для проверки подключения к базе данных
async def check_db_connection():
    try:
        connection = await aiomysql.connect(
            host=my_host,
            user=my_user,
            password=my_password,
            db=my_database
        )
        if connection:
            print("Успешное подключение к базе данных")
            return True
    except aiomysql.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
    return False


async def create_table_if_not_exists():
    try:
        connection = await aiomysql.connect(
            host=my_host,
            user=my_user,
            password=my_password,
            db=my_database
        )
        cursor = await connection.cursor()

        # SQL-запрос для создания таблицы
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            tg_id INT PRIMARY KEY,
            date DATE,
            name VARCHAR(255)
        );
        """
        await cursor.execute(create_table_query)
        await connection.commit()
        print("Таблица успешно создана или уже существует")
    except aiomysql.Error as e:
        print(f"Ошибка при создании таблицы: {e}")
    finally:
        if connection:
            await cursor.close()
            await connection.close()


async def user_exist(user_id: int):
    pass


async def add_user(user_id: int, role: str, registration_data):
    pass


async def get_admins() -> List[int]:
    pass
