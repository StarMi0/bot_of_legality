import asyncio
import datetime
import os
from typing import List

import aiomysql
from aiomysql import Connection

my_host = os.getenv('MYSQL_HOST', '77.232.134.200')
my_user = os.getenv('MYSQL_USER', 'root')
my_password = os.getenv('DB_ROOT_PASSWORD', '[legality_test]')
my_database = "urist_bot"


async def get_connection() -> Connection:
        connection = await aiomysql.connect(
            host=my_host,
            port=3306,
            user=my_user,
            password=my_password,
            db=my_database
        )
        return connection
# Функция для проверки подключения к базе данных
async def check_db_connection():
    try:
        connection = await get_connection()
        if connection:
            print("Успешное подключение к базе данных")
            return True
    except aiomysql.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
    return False





async def user_exist(user_id: int):
    try:
        connection = await get_connection()

        async with connection.cursor() as cur:
            await cur.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            result = await cur.fetchone()

        connection.close()
        return bool(result)
    except aiomysql.Error as e:
        print(f"Ошибка выборки пользователей: {e}")
    return False

async def add_user(user_id: int, user_name: str, role: str):
    try:
        connection = await get_connection()
        if role not in ['user', 'lawyer', 'admin']:
            role = 'user'
        reg_date = datetime.datetime.today().date()
        async with connection.cursor() as cur:
            await cur.execute("INSERT INTO users (user_id, user_name, registration_date, role)"
                              " VALUES (%s, %s, %s, %s)", (user_id, user_name, reg_date, role))
            await cur.execute("INSERT INTO user_info (user_id) VALUES (%s)", (user_id,))


        await connection.commit()
        connection.close()
        return True
    except aiomysql.Error as e:
        print(f"Ошибка добавления пользователя: {e}")
    return False


async def get_admins() -> List[int]:
    try:
        connection = await get_connection()
        async with connection.cursor() as cur:
            await cur.execute(
                "SELECT user_id FROM users WHERE role = 'admin'")
            admins = await cur.fetchall()

        connection.close()
        return admins
    except aiomysql.Error as e:
        print(f"Ошибка проверки админов: {e}")
    return []


async def get_user_role(user_id: int) -> str | None:
    try:
        connection = await get_connection()
        async with connection.cursor() as cur:
            await cur.execute(
                f"SELECT role FROM users WHERE user_id = {user_id}")
            role = await cur.fetchone()

        connection.close()
        print(role[0] if role else None)
        return role[0] if role else None
    except aiomysql.Error as e:
        print(f"Ошибка проверки админов: {e}")
    return None


async def add_order(order_id: str, user_id: int, lawyer_id: int | None, order_status: str, group_id: int):
    try:
        connection = await get_connection()

        async with connection.cursor() as cur:
            await cur.execute("INSERT INTO orders (order_id, user_id, lawyer_id, order_status, group_id)"
                              " VALUES (%s, %s, %s, %s, %s)", (order_id, user_id, lawyer_id, order_status, group_id))

        await connection.commit()
        connection.close()
        return True
    except aiomysql.Error as e:
        print(f"Ошибка добавления пользователя: {e}")
    return False

async def add_order_info(order_id: str, order_text: str, documents_id: str, order_cost: int,
                         order_day_start: datetime.date, order_day_end: datetime.date):
    try:
        connection = await get_connection()

        async with connection.cursor() as cur:
            await cur.execute("INSERT INTO orders (order_id, order_text, documents_id, order_cost, order_day_start, "
                              "order_day_end)"
                              "VALUES (%s, %s, %s, %s, %s, %s)",
                              (order_id, order_text, documents_id, order_cost, order_day_start, order_day_end))

        await connection.commit()
        connection.close()
        return True
    except aiomysql.Error as e:
        print(f"Ошибка добавления пользователя: {e}")
    return False


async def get_order_info_by_order_id(order_id: str) -> tuple | None:
    try:
        connection = await get_connection()
        async with connection.cursor() as cur:
            await cur.execute(
                f"SELECT user_id, lawyer_id, order_status FROM orders WHERE order_id = {order_id}")
            info = await cur.fetchone()

        connection.close()
        print(info)
        return info
    except aiomysql.Error as e:
        print(f"Ошибка получения информации по заказу: {e}")
    return None

async def get_order_additional_info_by_order_id(order_id: str) -> tuple | None:
    try:
        connection = await get_connection()
        async with connection.cursor() as cur:
            await cur.execute(
                f"SELECT order_text, documents_id, order_cost, order_day_start, order_day_end"
                f"FROM orders_info WHERE order_id = {order_id}")
            info = await cur.fetchone()

        connection.close()
        print(info)
        return info
    except aiomysql.Error as e:
        print(f"Ошибка получения дополнительной информации по заказу: {e}")
    return None



async def update_table(table_name: str, field_values: dict, where_clause: str):
    try:
        connection = await get_connection()

        async with connection.cursor() as cur:
            # Generate SET clause for SQL query
            set_clause = ", ".join([f"{field} = %s" for field in field_values.keys()])
            values = tuple(field_values.values())

            # Construct SQL query
            if where_clause:
                sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            else:
                sql = f"UPDATE {table_name} SET {set_clause}"

            # Execute the SQL query
            await cur.execute(sql, values)

        await connection.commit()
        connection.close()
    except aiomysql.Error as e:
        print(f"Ошибка добавления пользователя: {e}")
    return False

asyncio.run(update_table('users', {'user_name': 'Oleg'}, 'user_id=1111'))