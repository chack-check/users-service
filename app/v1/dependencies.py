from typing import Annotated, AsyncGenerator

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from app.project.db import session
from app.project.redis import redis_db
from app.v1.repositories.permissions import PermissionRepository
from app.v1.services.permissions import PermissionService

from .schemas import DbUser
from .services.users import UsersSet
from .services.verifications import Verificator

oauth2_scheme = HTTPBearer(auto_error=False)


class CustomContext(BaseContext):

    def __init__(self, users_set: UsersSet,
                 permission_service: PermissionService,
                 verificator: Verificator,
                 user: DbUser | None,
                 token: str | None):
        self.users_set = users_set
        self.permission_service = permission_service
        self.verificator = verificator
        self.user = user
        self.token = token


async def use_session() -> AsyncGenerator[AsyncSession, None]:
    async with session() as s:
        yield s
        await s.commit()


def use_users_set(
        session: Annotated[AsyncSession, Depends(use_session)]
) -> UsersSet:
    return UsersSet(session, redis_db)


def use_verificator() -> Verificator:
    return Verificator()


async def current_user(
        users_set: Annotated[UsersSet, Depends(use_users_set)],
        credentials: Annotated[HTTPAuthorizationCredentials | None,
                               Security(oauth2_scheme)],
) -> DbUser | None:
    if not credentials:
        return None

    return await users_set.get_from_token(credentials.credentials,
                                          raise_exception=False)


def use_permission_repository(session: Annotated[AsyncSession, Depends(use_session)]) -> PermissionRepository:
    return PermissionRepository(session=session)


def use_permission_service(permission_repository: Annotated[PermissionRepository, Depends(use_permission_repository)]) -> PermissionService:
    return PermissionService(repository=permission_repository)


def use_custom_context(
        users_set: Annotated[UsersSet, Depends(use_users_set)],
        permission_service: Annotated[PermissionService, Depends(use_permission_service)],
        verificator: Annotated[Verificator, Depends(use_verificator)],
        credentials: Annotated[HTTPAuthorizationCredentials | None,
                               Security(oauth2_scheme)],
        user: Annotated[DbUser | None, Depends(current_user)],
) -> CustomContext:
    return CustomContext(
        users_set, permission_service, verificator, user,
        credentials.credentials if credentials else None
    )


async def get_context(
        context: Annotated[CustomContext, Depends(use_custom_context)]
) -> CustomContext:
    return context
