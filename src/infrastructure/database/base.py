from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from infrastructure.settings import settings

engine = create_async_engine(settings.database_url, pool_recycle=900)  # Recycle pool every 15 minutes

session = async_sessionmaker(bind=engine)


class Base(DeclarativeBase): ...
