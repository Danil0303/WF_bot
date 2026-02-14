from sqlalchemy.orm import  DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from config import SettingConfig
engine = create_async_engine(url=SettingConfig.dp_path)
async_sessions = async_sessionmaker(engine, class_=AsyncSession)

class Base(AsyncAttrs, DeclarativeBase):
    pass