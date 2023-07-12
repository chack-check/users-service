from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from app.project.db import session
from app.project.redis import redis_db
from .services.users import UsersSet


class CustomContext(BaseContext):

    def __init__(self, users_set: UsersSet):
        self.users_set = users_set


async def use_session() -> AsyncSession:
    async with session() as s:
        yield s
        await s.commit()


def use_users_set(session: AsyncSession = Depends(use_session)):
    return UsersSet(session, redis_db)


def use_custom_context(users_set: UsersSet = Depends(use_users_set)) -> CustomContext:
    return CustomContext(users_set)


async def get_context(context: CustomContext = Depends(use_custom_context)) -> CustomContext:
    return context
