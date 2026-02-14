from datetime import datetime, timedelta
from typing import List
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql.psycopg import logger
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from app.db.base import connection
from app.db.databases import async_sessions
from app.db.model import Subscribe


@connection
async def get_user(session: async_sessions, id_user: int) -> Subscribe:
    result = await session.execute(
        select(Subscribe)
        .where(Subscribe.id_user == id_user)
    )
    user = result.scalar()
    return user

@connection
async def get_users_subscribe(session: async_sessions,subscribe: bool)->List[Subscribe]:
    result = await session.execute(
        select(Subscribe)
        .where(Subscribe.subscribe == subscribe)
    )
    user = result.scalars().all()
    return user

@connection
async def blocking(session: async_sessions, id_user: int, block: bool) -> bool:
    user = await get_user(id_user)
    if not user:
        logger.info(f"Пользователь с ID:{id_user} не найден!")
        return False
    try:
        await session.execute(update(Subscribe).filter_by(id_user=id_user).values(block=block))
        await session.commit()
        data = 'заблокирован' if block else 'доступ открыт'
        logger.success(f"Пользователь с ID:{id_user} {data}!")
        return True
    except SQLAlchemyError as exp:
        logger.error(exp)
        await session.rollback()
        return False


@connection
async def cancel_subscribe_db(session: async_sessions, id_user: int) -> bool:
    user = await get_user(id_user)
    if not user:
        logger.info(f"Пользователь с ID:{id_user} не найден!")
        return False
    try:
        await session.execute(update(Subscribe).filter_by(id_user=id_user).values(subscribe=False))
        await session.commit()
        logger.success(f"Пользователь с ID:{id_user} отменил подписку!")
        return True
    except SQLAlchemyError as exp:
        logger.error(exp)
        await session.rollback()
        return False

@connection
async def add_user(session: async_sessions, id_user: int, id_subscribe: str):
    user = await get_user(id_user)
    if user:
        logger.info(f'Пользователь {id_user} уже существует')
        return await update_date_subscribe(id_user, id_subscribe)
    try:
        data = datetime.today()
        user_new = Subscribe(id_user=id_user,
                             data_start=data,
                             data_end=data+timedelta(days=30),
                             subscribe=True,
                             id_subscribe=id_subscribe,
                             block=False
                             )
        session.add(user_new)
        await session.commit()
        logger.success(f"Зарегистрировал пользователя с ID {id_user}!")
    except (SQLAlchemyError, Exception)as exp:
        logger.error(exp)
        await session.rollback()

@connection
async def update_date_subscribe(session: async_sessions, user_id: int, id_subscribe: str):
    data = datetime.today()
    try:
        await session.execute(update(Subscribe).filter_by(id_user=user_id).values(data_start=data,
                                                                                  data_end=data+timedelta(days=30),
                                                                                  subscribe=True,
                                                                                  block=False,
                                                                                  id_subscribe=id_subscribe))
        await session.commit()
        logger.success(f'Данные пользователя обновлены: {user_id}')
    except SQLAlchemyError as exp:
        logger.error(exp)
        await session.rollback()

