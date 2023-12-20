import asyncio
import aiomysql
from utils.config import db_config


async def create_db():
    try:
        pool = await aiomysql.create_pool(**db_config)
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                query = "CREATE TABLE IF NOT EXISTS users (user_id INT PRIMARY KEY, role VARCHAR(255), registration_data TEXT)"
                await cursor.execute(query)

            await connection.commit()
    except Exception as e:
        print(f"Error creating database table: {e}")



asyncio.run(create_db())
