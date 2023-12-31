from datetime import datetime

from sqlalchemy.orm import mapped_column, Mapped

from app.project.db import Base
from .schemas import UserActivities


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    phone: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    middle_name: Mapped[str | None] = mapped_column(nullable=True)
    activity: Mapped[str] = mapped_column(default=UserActivities.offline.value)
    status: Mapped[str | None] = mapped_column(nullable=True)
    email_confirmed: Mapped[bool] = mapped_column(default=False)
    phone_confirmed: Mapped[bool] = mapped_column(default=False)
    last_seen: Mapped[datetime] = mapped_column(default=datetime.utcnow())
