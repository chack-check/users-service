from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.types import TIMESTAMP

from app.project.db import Base
from .schemas import UserActivities


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    avatar_url: Mapped[str] = mapped_column(server_default="https://google.com")
    phone: Mapped[str] = mapped_column(unique=True, nullable=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=True)
    password: Mapped[str] = mapped_column()
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    middle_name: Mapped[str | None] = mapped_column(nullable=True)
    activity: Mapped[str] = mapped_column(default=UserActivities.offline.value)
    status: Mapped[str | None] = mapped_column(nullable=True)
    email_confirmed: Mapped[bool] = mapped_column(default=False)
    phone_confirmed: Mapped[bool] = mapped_column(default=False)
    last_seen: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow().astimezone(ZoneInfo('UTC')),
    )
