import asyncio

import aiomysql
from utils.config import my_host, my_user, my_password, bot_db
from database.models import Base
from sqlalchemy.ext.asyncio import create_async_engine

# Настройки базы данных
DATABASE_URL = "mysql+aiomysql://user:password@host/database"


async def create_tables_if_not_exists():
    try:
        async with aiomysql.connect(my_host, my_user, my_password) as conn:
            async with conn.cursor() as cur:
                await cur.execute(f"CREATE DATABASE IF NOT EXISTS {bot_db}")
                # await cur.execute(f"DROP DATABASE {bot_db}")

            await conn.commit()
        engine = create_async_engine(
            f'mysql+aiomysql://{my_user}:{my_password}@{my_host}/{bot_db}')
        async with engine.connect() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()
        print("Таблицы успешно созданы или уже существуют")
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")

# asyncio.run(create_tables_if_not_exists())

#
# async def create_tables_if_not_exists():
#     try:
#         connection = await aiomysql.connect(
#             host=db_config.get('host'),
#             user=db_config.get('user'),
#             password=db_config.get('password'),
#             db=db_config.get('database')
#         )
#
#         async with connection.cursor() as cur:
#             # Create users table
#             await cur.execute("""CREATE DATABASE IF NOT EXISTS URIST_BOT""")
#
#             await cur.execute("""USE URIST_BOT""")
#             await cur.execute("""
#                 CREATE TABLE IF NOT EXISTS users (
#                     user_id VARCHAR(255) PRIMARY KEY,
#                     user_name VARCHAR(255),
#                     registration_date DATE,
#                     role VARCHAR(50) DEFAULT 'user'
#                 )
#             """)
#
#
#             # Create user_info table
#             await cur.execute("""
#                 CREATE TABLE IF NOT EXISTS user_info (
#                     user_id VARCHAR(255) PRIMARY KEY,
#                     passport_serial VARCHAR(255),
#                     passport_number VARCHAR(255),
#                     checking_account VARCHAR(255),
#                     FOREIGN KEY (user_id) REFERENCES users (user_id)
#                 )
#             """)
#
#             # Create orders table
#             await cur.execute("""
#                 CREATE TABLE IF NOT EXISTS orders (
#                     order_id VARCHAR(50) PRIMARY KEY,
#                     user_id VARCHAR(50),
#                     lawyer_id VARCHAR(50),
#                     order_status VARCHAR(50),
#                     group_id VARCHAR(255),
#                     FOREIGN KEY (user_id) REFERENCES users (user_id),
#                     FOREIGN KEY (lawyer_id) REFERENCES users (user_id)
#                 )
#             """)
#
#             # Create orders_info table
#             await cur.execute("""
#                 CREATE TABLE IF NOT EXISTS orders_info (
#                     order_id VARCHAR(50),
#                     order_text TEXT,
#                     documents_id VARCHAR(50),
#                     order_cost VARCHAR(255),
#                     order_day_start DATE,
#                     order_day_end DATE,
#                     message_id VARCHAR(50),
#                     group_id VARCHAR(50),
#                     FOREIGN KEY (order_id) REFERENCES orders (order_id)
#                 )
#             """)
#
#             await cur.execute("""
#                 CREATE TABLE IF NOT EXISTS offers (
#                     order_id VARCHAR(50),
#                     lawyer_id VARCHAR(50),
#                     order_cost VARCHAR(50),
#                     develop_time VARCHAR(50),
#                     FOREIGN KEY (order_id) REFERENCES orders (order_id)
#                 )
#             """)
#
#         # await connection.commit()
#         connection.close()
#         print("Таблица успешно создана или уже существует")
#     except aiomysql.Error as e:
#         print(f"Ошибка при создании таблицы: {e}")
#
# asyncio.run(create_tables_if_not_exists())
