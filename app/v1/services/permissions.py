from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from app.v1.exceptions import PermissionCategoryAlreadyExists
from app.v1.repositories.permissions import PermissionRepository
from app.v1.schemas import (
    CreatePermissionCategoryDto,
    CreatePermissionDto,
    PermissionCategoryDto,
    PermissionDto,
)


class PermissionService:

    def __init__(self, repository: PermissionRepository):
        self._repository = repository

    async def get_all(self) -> list[PermissionDto]:
        return await self._repository.get_all()

    async def create_category(self, category_data: CreatePermissionCategoryDto) -> PermissionCategoryDto:
        try:
            return await self._repository.create_category(category_data)
        except IntegrityError:
            raise PermissionCategoryAlreadyExists()

    async def create_permission(self, permission_data: CreatePermissionDto) -> PermissionDto:
        try:
            return await self._repository.create_permission(permission_data)
        except IntegrityError:
            raise PermissionCategoryAlreadyExists()

    async def get_by_codes(self, codes: list[str]) -> list[PermissionDto]:
        return await self._repository.get_by_codes(codes)
