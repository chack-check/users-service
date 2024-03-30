import logging

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1.models import Permission, PermissionCategory
from app.v1.schemas import (
    CreatePermissionCategoryDto,
    CreatePermissionDto,
    PermissionCategoryDto,
    PermissionDto,
)

logger = logging.getLogger("uvicorn.error")


class PermissionRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self) -> list[PermissionDto]:
        logger.debug(f"Fetching all permissions")
        stmt = select(Permission)
        result = await self._session.execute(stmt)
        result_list = result.scalars()
        logger.debug(f"Fetched all permissions count: {result_list}")
        return [PermissionDto.model_validate(perm) for perm in result_list]

    async def create_category(self, data: CreatePermissionCategoryDto) -> PermissionCategoryDto:
        logger.debug(f"Creating permissions category {data=}")
        stmt = insert(PermissionCategory).values(
            **data.model_dump(include={"code", "name"})
        ).returning(PermissionCategory)
        result = await self._session.execute(stmt)
        created_category = result.scalar_one()
        logger.debug(f"Created permissions category {created_category=}")
        return PermissionCategoryDto.model_validate(created_category)

    async def create_permission(self, data: CreatePermissionDto) -> PermissionDto:
        logger.debug(f"Creating permission: {data}")
        stmt = insert(Permission).values(
            **data.model_dump(include={"code", "name"})
        ).returning(Permission)
        result = await self._session.execute(stmt)
        created_permission = result.scalar_one()
        logger.debug(f"Created permission: {created_permission}")
        return PermissionDto.model_validate(created_permission)

    async def get_by_codes(self, codes: list[str]) -> list[PermissionDto]:
        logger.debug(f"Fetching permissions by codes: {codes=}")
        stmt = select(Permission).where(Permission.code.in_(codes))
        result = await self._session.execute(stmt)
        permissions = result.scalars().all()
        logger.debug(f"Fetched permissions by codes count: {len(permissions)}")
        return [PermissionDto.model_validate(perm) for perm in permissions]
