import aioredis
import pickle
from bot.utils.config import redis_host
from aioredis import Redis


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


async def get_temp_user_data(user_id):
    """
    Получение временных данных юриста из Redis.
    """
    redis = await aioredis.from_url(redis_host)
    if not redis:
        raise RuntimeError("Redis is not initialized. Call init_redis() first.")

    key = f"temp_lawyer:{user_id}"
    user_data = await redis.hgetall(key)

    if not user_data:
        return None

    # Преобразование данных из байтов в строки
    return {k.decode(): v.decode() for k, v in user_data.items()}


async def set_temp_user_data(user_id, data):
    """
    Сохранение временных данных юриста в Redis.
    """
    redis = await aioredis.from_url(redis_host)
    if not redis:
        raise RuntimeError("Redis is not initialized. Call init_redis() first.")

    key = f"temp_lawyer:{user_id}"
    await redis.hset(key, mapping=data)


async def delete_temp_user_data(user_id):
    """
    Удаление временных данных юриста из Redis.
    """
    redis = await aioredis.from_url(redis_host)
    if not redis:
        raise RuntimeError("Redis is not initialized. Call init_redis() first.")

    key = f"temp_lawyer:{user_id}"
    await redis.delete(key)


async def check_redis_connection(redis_host: str, redis_port: int):
    try:
        # Создаем объект Redis с указанием хоста и порта
        redis = Redis(host=redis_host, port=redis_port)

        # Выполняем команду PING для проверки соединения
        response = await redis.ping()
        if response:
            print("Redis подключен: PONG")
            return True
    except Exception as e:
        print(f"Ошибка подключения к Redis: {e}")
        return False
    finally:
        await redis.close()