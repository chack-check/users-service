from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP

from app.project.db import Base

from .schemas import UserActivities


class UserAvatar(Base):
    __tablename__ = "users_avatars"

    id: Mapped[int] = mapped_column(primary_key=True)
    original_url: Mapped[str] = mapped_column()
    original_filename: Mapped[str] = mapped_column()
    converted_url: Mapped[str] = mapped_column(nullable=True)
    converted_filename: Mapped[str] = mapped_column(nullable=True)
    users: Mapped[list["User"]] = relationship(back_populates="avatar")


class PermissionCategory(Base):
    __tablename__ = "permission_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column()
    permissions: Mapped[list["Permission"]] = relationship(back_populates="category")


user_permission = Table(
    "user_permissions",
    Base.metadata,

    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),
)


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column()
    category_id: Mapped[int | None] = mapped_column(ForeignKey(PermissionCategory.id), nullable=True)
    category: Mapped[PermissionCategory] = relationship(lazy="selectin", back_populates="permissions")
    users: Mapped[list["User"]] = relationship(secondary=user_permission, back_populates="permissions")


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    avatar_id: Mapped[int] = mapped_column(ForeignKey(UserAvatar.id), nullable=True)
    avatar: Mapped["UserAvatar"] = relationship(back_populates="users", lazy='selectin')
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
        default=datetime.now().astimezone(ZoneInfo('UTC')),
    )
    permissions: Mapped[list[Permission]] = relationship(secondary=user_permission, back_populates="users", lazy="selectin")
