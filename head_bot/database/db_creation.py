import asyncio

import aiomysql
from loguru import logger

from utils.config import my_host, my_user, my_password, bot_db, my_database, DATABASE_URL, DATABASE_URL_CREATE
from database.models import Base
from sqlalchemy.ext.asyncio import create_async_engine

# Настройки базы данных


# async def create_tables_if_not_exists():
#     conn = await aiomysql.connect(DATABASE_URL_CREATE)
#     try:
#         await conn.execute(f"CREATE DATABASE {bot_db}")
#     #     await conn.execute("DROP TABLE offers CASCADE")
#     #     await conn.close()
#     except Exception as e:
#         logger.error(e)
#     try:
#         engine = create_async_engine(
#             DATABASE_URL)
#
#         async with engine.begin() as conn:
#             await conn.run_sync(Base.metadata.create_all)
#         await engine.dispose()
#         print("Таблицы успешно созданы или уже существуют")
#     except Exception as e:
#         print(f"Ошибка при создании таблиц: {e}")
async def create_tables_if_not_exists():
    conn = await aiomysql.connect(user=my_user, password=my_password, host=my_host)
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(f"CREATE DATABASE IF NOT EXISTS {bot_db}")
        await conn.commit()
    except Exception as e:
        logger.error(f"Ошибка при создании базы данных: {e}")
    finally:
        conn.close()

    try:
        engine = create_async_engine(DATABASE_URL)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()
        print("Таблицы успешно созданы или уже существуют")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")

asyncio.run(create_tables_if_not_exists())
