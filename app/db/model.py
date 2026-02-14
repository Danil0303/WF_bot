from datetime import datetime

from app.db.databases import Base
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import BigInteger, DateTime, BOOLEAN, String

class Subscribe(Base):
    __tablename__ = 'subscribe'
    id_user: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    data_start: Mapped[datetime] = mapped_column(DateTime)
    data_end: Mapped[datetime] = mapped_column(DateTime)
    subscribe: Mapped[bool] = mapped_column(BOOLEAN)
    id_subscribe: Mapped[bool] = mapped_column(String)
    block: Mapped[bool]=mapped_column(BOOLEAN)