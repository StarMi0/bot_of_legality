import aiomysql
from loguru import logger

from database.models import Base
from sqlalchemy.ext.asyncio import create_async_engine


async def create_tables_if_not_exists(db_host, db_user, db_password, db_database, clear=False):
    """
    Создает таблицы в БД на основе моделей
    Если clear=True, то сначала удаляет существующую базу данных.
    """
    base_url = f"mysql+aiomysql://{db_user}:{db_password}@{db_host}:3306/"
    db_url = f"{base_url}{db_database}"

    logger.info(f"Подключение к MySQL: host={db_host}, user={db_user}, database={db_database}")
    print(f"Попытка подключения: {db_host=} {db_user=} {db_database=} {db_password}")

    try:
        # Подключение без указания базы данных
        connection = await aiomysql.connect(
            host=db_host, user=db_user, password=db_password
        )
        logger.info("Подключение к серверу MySQL установлено")

        async with connection.cursor() as cursor:
            if clear:
                # Удаление базы данных, если она существует
                await cursor.execute(f"DROP DATABASE IF EXISTS `{db_database}`")
                print(f"База данных {db_database} удалена")

            # Создание базы данных
            await cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_database}`")
            print(f"База данных {db_database} создана или уже существует")

        await connection.ensure_closed()
    except Exception as e:
        logger.error(f"Ошибка при работе с базой данных: {e}")
        return

        # Создание таблиц
    try:
        engine = create_async_engine(db_url, echo=True)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        await engine.dispose()
        print("Таблицы успешно созданы или уже существуют")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        print(f"Ошибка при создании таблиц: {e}")
