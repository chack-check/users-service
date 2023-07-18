from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from app.project.db import session
from app.project.redis import redis_db
from .services.users import UsersSet
from .schemas import DbUser


oauth2_scheme = HTTPBearer(auto_error=False)


class CustomContext(BaseContext):

    def __init__(self, users_set: UsersSet, user: DbUser | None):
        self.users_set = users_set
        self.user = user


async def use_session() -> AsyncSession:
    async with session() as s:
        yield s
        await s.commit()


def use_users_set(
        session: Annotated[AsyncSession, Depends(use_session)]
) -> UsersSet:
    return UsersSet(session, redis_db)


async def current_user(
        users_set: Annotated[UsersSet, Depends(use_users_set)],
        credentials: Annotated[HTTPAuthorizationCredentials | None,
                               Security(oauth2_scheme)],
) -> DbUser | None:
    if not credentials:
        return None

    return await users_set.get_from_token(credentials.credentials,
                                          raise_exception=False)


def use_custom_context(
        users_set: Annotated[UsersSet, Depends(use_users_set)],
        user: Annotated[DbUser | None, Depends(current_user)],
) -> CustomContext:
    return CustomContext(users_set, user)


async def get_context(
        context: Annotated[CustomContext, Depends(use_custom_context)]
) -> CustomContext:
    return context
