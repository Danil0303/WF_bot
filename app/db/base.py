import functools

from loguru import logger

from app.db.databases import engine, Base, async_sessions

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def connection(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        async with async_sessions() as session:
            return await func(session, *args, **kwargs)
    return wrapper