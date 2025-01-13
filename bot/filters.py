from asyncio import Lock
import aioschedule as schedule
import asyncio
from datetime import datetime


class IsAdmin:
    """Фильтр для проверки, является ли пользователь администратором"""

    def __init__(self, db_pool, table_name: str = "administrators") -> None:
        """
        Инициализация фильтра
        :param db_pool: Пул соединений с MySQL
        :param table_name: Имя таблицы в базе данных
        """
        self.admins = []
        self.db_pool = db_pool
        self.table_name = table_name
        self.lock = Lock()

    async def load_admins(self) -> list:
        """
        Загрузка списка администраторов из базы данных и возврат списка.
        """
        query = f"SELECT id FROM {self.table_name}"
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                result = await cursor.fetchall()
                async with self.lock:
                    self.admins = [row[0] for row in result]
        return self.admins

    async def update_admins(self) -> None:
        """
        Проверка базы данных на новые ID администраторов и обновление списка.
        """
        await self.load_admins()

    def schedule_updates(self):
        """
        Настройка ежедневного обновления списка администраторов в 12:00.
        """
        schedule.every().day.at("12:00").do(asyncio.create_task, self.update_admins())

    async def start_scheduler(self):
        """
        Запуск планировщика.
        """
        while True:
            await schedule.run_pending()
            await asyncio.sleep(1)


class IsUser:
    """Фильтр для проверки, является ли пользователь пользователем"""

    def __init__(self, db_pool, table_name: str = "users") -> None:
        """
        Инициализация фильтра
        :param db_pool: Пул соединений с MySQL
        :param table_name: Имя таблицы в базе данных
        """
        self.users = []
        self.db_pool = db_pool
        self.table_name = table_name
        self.lock = Lock()

    async def load_users(self) -> list:
        """
        Загрузка списка администраторов из базы данных и возврат списка.
        """
        query = f"SELECT tg_id FROM {self.table_name}"
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                result = await cursor.fetchall()
                async with self.lock:
                    self.users = [row[0] for row in result]
        return self.users

    async def update_ids(self, tg_id) -> list:
        self.users.append(tg_id)
        return self.users

    async def add_user(self, tg_id: int, name: str, date: str) -> None:
        """
        Добавление нового пользователя в базу данных и добавление его id в список id пользователей
        Дата преобразуется из формата дд.мм.гггг в формат гггг-мм-дд.
        """

        # Преобразование даты
        try:
            formatted_date = datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("Неверный формат даты. Используйте формат: дд.мм.гггг")

        query = f"INSERT INTO lawyers (tg_id, name, date) VALUES (%s, %s, %s)"
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, (tg_id, name, formatted_date))
                await conn.commit()
        await self.update_ids(tg_id)
