import asyncio

import aioredis
import pickle
from utils.config import redis_host


async def add_to_redis(name, data):
    # Подключение к Redis
    redis = await aioredis.from_url(redis_host)
    # Обновление кэша в Redis
    await redis.set(name, data)
    # Закрытие соединения с Redis
    await redis.close()


async def add_list_to_redis(name, data):
    # Подключение к Redis
    redis = await aioredis.from_url(redis_host)
    # Обновление кэша в Redis
    await redis.set(name, pickle.dumps(data))
    # Закрытие соединения с Redis
    await redis.close()


async def get_from_redis(name):
    redis = await aioredis.from_url(redis_host)
    result = await redis.get(name)
    await redis.close()
    return result


async def get_list_from_redis(name):
    redis = await aioredis.from_url(redis_host)
    result = await redis.get(name)
    await redis.close()
    r = pickle.loads(result) if result else None
    return r


async def delete_from_redis(name):
    redis = await aioredis.from_url(redis_host)
    await redis.delete(name)
    await redis.close()


# asyncio.run(add_to_redis(123, [(1,2)]))