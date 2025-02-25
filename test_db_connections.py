import os
import asyncio
import aiomysql
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base

load_dotenv(find_dotenv())
# Импорт переменных из окружения
my_host = os.getenv('MYSQL_HOST')
my_user = os.getenv('MYSQL_USER')
my_password = os.getenv('DB_ROOT_PASSWORD')
my_database = "legality"

Base = declarative_base()

async def test_aiomysql_connection():
    """Проверка подключения через aiomysql"""
    print(f"Тест aiomysql: host={my_host}, user={my_user}, database={my_database}")
    try:
        connection = await aiomysql.connect(
            host=my_host, user=my_user, password=my_password, db=my_database
        )
        print("✅ Подключение через aiomysql успешно!")
        await connection.ensure_closed()
    except Exception as e:
        print(f"❌ Ошибка при подключении через aiomysql: {e}")

async def test_sqlalchemy_connection():
    """Проверка подключения через SQLAlchemy"""
    db_url = f"mysql+aiomysql://{my_user}:{my_password}@{my_host}/{my_database}"
    print(f"Тест SQLAlchemy: {db_url}")
    try:
        engine = create_async_engine(db_url, echo=True)
        async with engine.begin() as conn:
            print("✅ Подключение через SQLAlchemy успешно!")
        await engine.dispose()
    except Exception as e:
        print(f"❌ Ошибка при подключении через SQLAlchemy: {e}")

async def main():
    await test_aiomysql_connection()
    await test_sqlalchemy_connection()

if __name__ == "__main__":
    asyncio.run(main())