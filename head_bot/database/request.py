import asyncio
import datetime
from typing import List, Optional, Tuple
import aiomysql
from loguru import logger
from sqlalchemy import AsyncAdaptedQueuePool, select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from database.models import User, UserInfo, Order, OrderInfo, Offer, EducationDocument, LawyerInfo, OrderDocuments
from utils.config import bot_db, my_password, my_user, my_host, DATABASE_URL


async def get_connection():
    engine = create_async_engine(
        DATABASE_URL,
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
            result = await session.execute(select(User).filter_by(user_id=str(user_id)))
            user = result.scalar_one_or_none()
            return user is not None


async def add_lawyer_info(user_id: str, education: str):
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                new_lawyer_info = LawyerInfo(user_id=str(user_id), education=education
                                             )
                session.add(new_lawyer_info)

            await session.commit()
            return True
    except Exception as e:
        logger.error(f"Ошибка добавления информации о юристе: {e}")
        return False
    finally:
        await engine.dispose()


async def add_user(user_id: str, user_name: str, user_fio: str, user_date_birth: str, role: str):
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                # Создаем новый экземпляр модели User
                new_user = User(
                    user_id=str(user_id),
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


async def get_admins() -> List[str]:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(select(User).filter_by(role='admin'))
                admins = result.scalars().all()
                return [admin.user_id for admin in admins]
    except Exception as e:
        logger.error(f"Ошибка проверки админов: {e}")
        return []


async def get_user_role(user_id: str) -> str | None:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(select(User.role).filter_by(user_id=str(user_id)))
                role = result.scalar_one_or_none()
                return role if role else None
    except Exception as e:
        logger.error(f"Ошибка получения роли пользователя: {e}")
        return None


async def get_user_info(user_id: str) -> str | None:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(select(User.user_name, User.role).filter_by(user_id=str(user_id)))
                role = result.fetchone()
                return role
    except Exception as e:
        logger.error(f"Ошибка получения роли пользователя: {e}")
        return None


async def add_order(order_id: str, user_id: str, lawyer_id: str | None, order_status: str, group_id: str) -> int:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                # Проверка наличия активного заказа
                active_order = await session.execute(
                    select(Order).where(Order.user_id == str(user_id), Order.order_status != 'close')
                )
                active_order = active_order.scalar_one_or_none()

                if active_order:
                    return 2

                # Если активного заказа нет, добавляем новый заказ
                new_order = Order(
                    order_id=order_id,
                    user_id=str(user_id),
                    lawyer_id=lawyer_id,
                    order_status=order_status,
                    group_id=group_id
                )
                session.add(new_order)

            await session.commit()
            return 0  # Успешное добавление заказа
    except Exception as e:
        logger.error(f"Ошибка добавления заказа: {e}")
        return 1  # Ошибка добавления заказа
    finally:
        await engine.dispose()


async def add_order_info(order_id: str, order_text: str, documents_id: list[str], order_cost: Optional[str],
                         order_day_start: Optional[datetime.date], order_day_end: Optional[datetime.date],
                         message_id: str,
                         group_id: str) -> bool:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                new_order_info = OrderInfo(
                    order_id=order_id,
                    order_text=order_text,
                    order_cost=order_cost,
                    order_day_start=order_day_start,
                    order_day_end=order_day_end,
                    message_id=message_id,
                    group_id=group_id
                )
                session.add(new_order_info)

                # Добавление документов
                if documents_id:
                    for doc_id in documents_id:
                        new_order_document = OrderDocuments(
                            order_id=order_id,
                            document_id=doc_id
                        )
                        session.add(new_order_document)

            await session.commit()
            return True
    except Exception as e:
        logger.error(f"Ошибка внесения дополнительной информации: {e}")
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
        logger.error(f"Ошибка получения информации по заказу: {e}")
        return None


async def get_order_additional_info_by_order_id(order_id: str) -> Optional[Tuple]:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(
                    select(
                        OrderInfo.order_text,
                        OrderInfo.order_cost,
                        OrderInfo.order_day_start,
                        OrderInfo.order_day_end,
                        OrderInfo.message_id,
                        OrderInfo.group_id,
                        OrderDocuments.document_id
                    ).join(OrderDocuments, OrderInfo.order_id == OrderDocuments.order_id,
                           isouter=True)  # Use isouter=True for a left join
                    .filter(OrderInfo.order_id == order_id)
                )

                info = result.all()
                if not info:
                    return None

                order_info = info[0]
                documents = [row.document_id for row in info if
                             row.document_id is not None]  # Handle cases where document_id might be None

                return (
                    order_info.order_text,
                    documents,
                    order_info.order_cost,
                    order_info.order_day_start,
                    order_info.order_day_end,
                    order_info.message_id,
                    order_info.group_id
                )
    except Exception as e:
        logger.error(f"Ошибка получения дополнительной информации по заказу: {e}")
        return None


async def get_active_order(user_id: str) -> str | None:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(
                    select(Order.order_id).where(Order.user_id == str(user_id), Order.order_status != 'close')
                )
                order_id = result.scalar_one_or_none()

        return order_id if order_id else False
    except Exception as e:
        logger.error(f"Ошибка получения активного заказа: {e}")
        return True


async def get_active_order_by_lawyer(user_id: str) -> list:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(
                    select(Order.order_id).where(Order.lawyer_id == str(user_id), Order.order_status != 'close')
                )
                order_id = result.fetchall()

        return [i for i in order_id[0]]
    except Exception as e:
        logger.error(f"Ошибка получения активного заказа: {e}")
        return []


async def get_active_order_lawyer_id(user_id: str) -> str | None:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(
                    select(Order.lawyer_id).filter_by(user_id=str(user_id))
                )
                lawyer_id = result.scalar_one_or_none()

        return lawyer_id if lawyer_id else None
    except Exception as e:
        logger.error(f"Ошибка получения ID исполнителя: {e}")
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
                        stmt = stmt.where(getattr(table, key) == value)

                # Execute the SQL query
                await session.execute(stmt)

            await session.commit()
    except Exception as e:
        logger.error(f"Ошибка обновления таблицы: {e}")
    return False


async def add_offer(offer_id: str, order_id: str, lawyer_id: str, order_cost: int, develop_time: int):
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                new_offer = Offer(
                    offer_id=offer_id,
                    order_id=order_id,
                    lawyer_id=str(lawyer_id),
                    order_cost=order_cost,
                    develop_time=develop_time
                )
                session.add(new_offer)

            await session.commit()
    except Exception as e:
        logger.error(f"Ошибка добавления предложения: {e}")


async def get_offer_by_offer_id(offer_id: str) -> list | None:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(
                    select(Offer.order_id, Offer.lawyer_id, Offer.order_cost, Offer.develop_time).filter_by(
                        offer_id=offer_id)
                )
                offers = result.fetchone()

        return offers if offers else None
    except Exception as e:
        logger.error(f"Ошибка получения предложений: {e}")
        return None


async def get_offers_by_lawyer_order_id(lawyer_id: str, order_id: str) -> list | None:
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(
                    select(Offer.lawyer_id, Offer.order_cost, Offer.develop_time).filter(Offer.order_id == order_id,
                                                                                         Offer.lawyer_id == lawyer_id)
                )
                offers = result.fetchone()

        return offers if offers else None
    except Exception as e:
        logger.error(f"Ошибка получения предложений: {e}")
        return None


async def add_document(user_id, document_data):
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                new_document = EducationDocument(user_id=str(user_id), document=document_data)
                session.add(new_document)

            await session.commit()
    except Exception as e:
        logger.error(f"Ошибка добавления файла: {e}")
    finally:
        await engine.dispose()


async def add_order_document(user_id, document_data):
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                new_document = EducationDocument(user_id=str(user_id), document=document_data)
                session.add(new_document)

            await session.commit()
    except Exception as e:
        logger.error(f"Ошибка добавления файла: {e}")
    finally:
        await engine.dispose()


async def get_order_document(document_id, order_id):
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                new_document = OrderDocuments(document_id=str(document_id), order_id=order_id)
                session.add(new_document)

            await session.commit()
            return 0
    except Exception as e:
        logger.error(f"Ошибка добавления файла: {e}")
        return 1
    finally:
        await engine.dispose()


async def get_documents(order_id):
    engine = await get_connection()

    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(
                    select(OrderDocuments.document_id)
                    .filter(OrderDocuments.order_id == str(order_id))
                )
                documents = result.fetchall()

        return [doc[0] for doc in documents]
    except Exception as e:
        logger.error(f"Ошибка получения файла: {e}")
    finally:
        await engine.dispose()


# asyncio.run(get_user_role('12345'))
# print(print(asyncio.run(add_order(order_id='1241252152', user_id='6903479498', lawyer_id=None, order_status='in_search',
#                                   group_id='12412412'))))
# asyncio.run(add_order_info(order_id='412142124412', order_text='123123', documents_id=['123123','12313'], order_cost=None,
#                              order_day_start=None, order_day_end=None, message_id='123123,123123', group_id='213213'))


print(asyncio.run(update_table(Order, field_values={'order_status': 'close'
                                                        },
                               where_clause={f'order_id': 'bd1feeb5b6f649b78a72fd00f7c2abbd'})))
#
# print(getattr(OrderInfo, 'order_id'))
# print(asyncio.run(get_order_additional_info_by_order_id('e89b422b6eed42038e3976b5b291c77b')))
# print(asyncio.run(get_active_order('6903479498')))
