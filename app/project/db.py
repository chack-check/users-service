from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .settings import settings


engine = create_async_engine(settings.database_url)

session = async_sessionmaker(bind=engine)


class Base(DeclarativeBase):
    ...
