import datetime
from typing import List
import aiomysql
from loguru import logger
from sqlalchemy import AsyncAdaptedQueuePool, select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from database.models import User, UserInfo, Order, OrderInfo, Offer, EducationDocument, LawyerInfo
from utils.config import bot_db, my_password, my_user, my_host


async def get_connection():
    engine = create_async_engine(
        f'mysql+aiomysql://{my_user}:{my_password}@{my_host}/{bot_db}',
        poolclass=AsyncAdaptedQueuePool,  # Указываем класс пула соединений
        pool_size=5,  # Размер пула соединений (по умолчанию)
        max_overflow=10,  # Максимальное количество временных соединений, создаваемых при перегрузке
        pool_timeout=30,  # Время ожидания в секундах перед возбуждением исключения
        pool_recycle=300
    )

    return engine


async def user_exist(user_id: str) -> bool:
    engine = await get_connection()

    async with AsyncSession(engine) as session:
        async with session.begin():
            result = await session.execute(select(User).filter_by(user_id=user_id))
            user = result.scalar_one_or_none()
            return user is not None


async def add_lawyer_info(user_id: int, education: str, education_documents: str):
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                new_lawyer_info = LawyerInfo(user_id=user_id, education=education, education_documents=education_documents)
                session.add(new_lawyer_info)

            await session.commit()
            return True
    except Exception as e:
        logger.error(f"Ошибка добавления информации о юристе: {e}")
        return False
    finally:
        await engine.dispose()


async def add_user(user_id: int, user_name: str, user_fio: str, user_date_birth: str, role: str):
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                # Создаем новый экземпляр модели User
                new_user = User(
                    user_id=user_id,
                    user_name=user_name,
                    user_fio=user_fio,
                    user_date_birth=user_date_birth,
                    registration_date=datetime.date.today(),
                    role=role
                )
                # Добавляем пользователя в сессию
                session.add(new_user)

            # Коммитим транзакцию
            await session.commit()
            return True
    except Exception as e:
        logger.error(f"Ошибка добавления пользователя: {e}")
        return False
    finally:
        await engine.dispose()


async def add_lawyer_info(user_id: int, education: str, education_documents: str):
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                # Создаем новый экземпляр модели LawyerInfo
                new_lawyer_info = LawyerInfo(
                    user_id=user_id,
                    education=education,
                    education_documents=education_documents
                )
                # Добавляем информацию о юристе в сессию
                session.add(new_lawyer_info)

            # Коммитим транзакцию
            await session.commit()
            return True
    except Exception as e:
        logger.error(f"Ошибка добавления информации о юристе: {e}")
        return False
    finally:
        await engine.dispose()


async def get_admins() -> List[str]:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(select(User).filter_by(role='admin'))
                admins = result.scalars().all()
                return [admin.user_id for admin in admins]
    except Exception as e:
        print(f"Ошибка проверки админов: {e}")
        return []


async def get_user_role(user_id: str) -> str | None:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(select(User.role).filter_by(user_id=user_id))
                role = result.scalar_one_or_none()
                return role if role else None
    except Exception as e:
        print(f"Ошибка получения роли пользователя: {e}")
        return None


async def add_order(order_id: str, user_id: int, lawyer_id: str | None, order_status: str, group_id: str) -> int:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                # Проверка наличия активного заказа
                active_order = await session.execute(
                    select(Order).where(Order.user_id == user_id, Order.order_status != 'done')
                )
                active_order = active_order.scalar_one_or_none()

                if active_order:
                    return 2

                # Если активного заказа нет, добавляем новый заказ
                new_order = Order(
                    order_id=order_id,
                    user_id=user_id,
                    lawyer_id=lawyer_id,
                    order_status=order_status,
                    group_id=group_id
                )
                session.add(new_order)

            await session.commit()
            return 1  # Успешное добавление заказа
    except Exception as e:
        print(f"Ошибка добавления заказа: {e}")
        return 0  # Ошибка добавления заказа
    finally:
        await engine.dispose()


async def add_order_info(order_id: str, order_text: str, documents_id: str, order_cost: str | None,
                         order_day_start: datetime.date | None, order_day_end: datetime.date | None, message_id: str,
                         group_id: str) -> bool:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                new_order_info = OrderInfo(
                    order_id=order_id,
                    order_text=order_text,
                    documents_id=documents_id,
                    order_cost=order_cost,
                    order_day_start=order_day_start,
                    order_day_end=order_day_end,
                    message_id=message_id,
                    group_id=group_id
                )
                session.add(new_order_info)

            await session.commit()
            return True
    except Exception as e:
        print(f"Ошибка внесения дополнительной информации: {e}")
        return False


async def get_order_info_by_order_id(order_id: str) -> tuple | None:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(
                    select(Order.user_id, Order.lawyer_id, Order.order_status).filter_by(order_id=order_id)
                )
                info = result.one_or_none()
        return info
    except Exception as e:
        print(f"Ошибка получения информации по заказу: {e}")
        return None


async def get_order_additional_info_by_order_id(order_id: str) -> tuple | None:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(
                    select(
                        OrderInfo.order_text, OrderInfo.documents_id, OrderInfo.order_cost,
                        OrderInfo.order_day_start, OrderInfo.order_day_end, OrderInfo.message_id,
                        OrderInfo.group_id
                    ).filter_by(order_id=order_id)
                )
                info = result.one_or_none()

        return info
    except Exception as e:
        print(f"Ошибка получения дополнительной информации по заказу: {e}")
        return None


async def get_active_order(user_id: str) -> str | None:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(
                    select(Order.order_id).filter_by(user_id=user_id)
                )
                order_id = result.scalar_one_or_none()

        return order_id if order_id else None
    except Exception as e:
        print(f"Ошибка получения активного заказа: {e}")
        return None


async def get_active_order_lawyer_id(user_id: str) -> str | None:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(
                    select(Order.lawyer_id).filter_by(user_id=user_id)
                )
                lawyer_id = result.scalar_one_or_none()

        return lawyer_id if lawyer_id else None
    except Exception as e:
        print(f"Ошибка получения ID исполнителя: {e}")
        return None


async def update_table(table, field_values: dict, where_clause: dict):
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = update(table).values(**field_values)

                # Apply where clause
                if where_clause:
                    for key, value in where_clause.items():
                        stmt = stmt.where(getattr(table.c, key) == value)

                # Execute the SQL query
                await session.execute(stmt)

            await session.commit()
    except Exception as e:
        print(f"Ошибка обновления таблицы: {e}")
    return False


async def add_offer(order_id: str, lawyer_id: int, order_cost: int, develop_time: int):
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                new_offer = Offer(
                    order_id=order_id,
                    lawyer_id=lawyer_id,
                    order_cost=order_cost,
                    develop_time=develop_time
                )
                session.add(new_offer)

            await session.commit()
    except Exception as e:
        print(f"Ошибка добавления предложения: {e}")


async def get_offers_by_order_id(order_id: str) -> list | None:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(
                    select(Offer.lawyer_id, Offer.order_cost, Offer.develop_time).filter_by(order_id=order_id)
                )
                offers = result.fetchone()

        return offers if offers else None
    except Exception as e:
        print(f"Ошибка получения предложений: {e}")
        return None


async def add_document(user_id, document_data):
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                new_document = EducationDocument(user_id=user_id, document=document_data)
                session.add(new_document)

            await session.commit()
    except Exception as e:
        logger.error(f"Ошибка добавления файла: {e}")
    finally:
        await engine.dispose()


async def get_document(user_id):
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(
                    select(EducationDocument.document)
                    .filter(EducationDocument.user_id == user_id)
                )
                document = result.scalar_one_or_none()

        return document
    except Exception as e:
        logger.error(f"Ошибка получения файла: {e}")
    finally:
        await engine.dispose()

