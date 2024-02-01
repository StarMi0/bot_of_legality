import asyncio
import os

import aiomysql
from utils.config import db_config

my_host = os.getenv('MYSQL_HOST', '77.232.134.200')
my_user = os.getenv('MYSQL_USER', 'root')
my_password = os.getenv('DB_ROOT_PASSWORD', '[legality_test]')
my_database = "mysql"


async def create_tables_if_not_exists():
    try:
        connection = await aiomysql.connect(
            host=my_host,
            user=my_user,
            password=my_password,
            db=my_database
        )

        async with connection.cursor() as cur:
            # Create users table
            await cur.execute("""CREATE DATABASE IF NOT EXISTS URIST_BOT""")

            await cur.execute("""USE URIST_BOT""")
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    user_name VARCHAR(255),
                    registration_date DATE,
                    role VARCHAR(50) DEFAULT 'user'
                )
            """)


            # Create user_info table
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS user_info (
                    user_id BIGINT PRIMARY KEY,
                    passport_serial INT,
                    passport_number INT,
                    checking_account INT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            # Create orders table
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id VARCHAR(50) PRIMARY KEY,
                    user_id BIGINT,
                    lawyer_id BIGINT,
                    order_status VARCHAR(50),
                    group_id BIGINT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (lawyer_id) REFERENCES users (user_id)
                )
            """)

            # Create orders_info table
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS orders_info (
                    order_id VARCHAR(50),
                    order_text TEXT,
                    documents_id VARCHAR(50),
                    order_cost BIGINT,
                    order_day_start DATE,
                    order_day_end DATE,
                    FOREIGN KEY (order_id) REFERENCES orders (order_id)
                )
            """)

            await cur.execute("""
                CREATE TABLE IF NOT EXISTS offers (
                    order_id VARCHAR(50),
                    lawyer_id BIGINT,
                    order_cost BIGINT,
                    develop_time BIGINT,
                    FOREIGN KEY (order_id) REFERENCES orders (order_id)
                )
            """)

        # await connection.commit()
        connection.close()
        print("Таблица успешно создана или уже существует")
    except aiomysql.Error as e:
        print(f"Ошибка при создании таблицы: {e}")

asyncio.run(create_tables_if_not_exists())
