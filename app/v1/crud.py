from sqlalchemy.orm import mapped_column, Mapped

from app.project.db import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    middle_name: Mapped[str | None] = mapped_column(nullable=True)
    activity: Mapped[str] = mapped_column()
    status: Mapped[str | None] = mapped_column(nullable=True)
