import logging
import math
import re
from dataclasses import asdict, fields
from typing import Any, Generic, NamedTuple, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import Select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1.constants import UserPermissionsEnum
from app.v1.graphql.graph_types import AuthData

from .exceptions import (
    AuthenticationEmailOrPhoneRequired,
    AuthRequired,
    PermissionRequired,
    UserWithThisEmailAlreadyExists,
    UserWithThisPhoneAlreadyExists,
    UserWithThisUsernameAlreadyExists,
)
from .schemas import DbUser

T = TypeVar('T')

K = TypeVar('K', bound=BaseModel)

logger = logging.getLogger("uvicorn.error")


class PaginatedData(NamedTuple, Generic[K]):
    page: int
    num_pages: int
    per_page: int
    data: list[K]


def validate_auth_data(data: AuthData) -> None:
    logger.debug(f"Validating authentication data: {data=}")
    if not data.email and not data.phone:
        logger.warning(f"Authentication data not specified email nor phone: {data=}")
        raise AuthenticationEmailOrPhoneRequired


def validate_user_required(user: DbUser | None) -> None:
    logger.debug(f"Validating user required {user=}")
    if not user:
        logger.warning(f"Authentication validation invalid: auth required")
        raise AuthRequired()


def validate_user_permissions(user: DbUser, permissions: list[UserPermissionsEnum]) -> None:
    logger.debug(f"Validating user permissions: {user=} {permissions=}")
    if not set(permissions).issubset([perm.code for perm in user.permissions]):
        logger.warning(f"User has no permissions {user=} {permissions=}")
        raise PermissionRequired([perm.value for perm in permissions])


def get_schema_from_pydantic(schema, model: K):
    logger.debug(f"Getting schema from pydantic {schema=} {model=}")
    include_fields = {field.name for field in fields(schema)}
    return schema(**model.model_dump(include=include_fields))


def get_pydantic_from_schema(schema, model: Type[K]) -> K:
    logger.debug(f"Getting pydantic from schema {schema=} {model=}")
    return model.model_validate(asdict(schema))


def to_dict(schema, *, exclude_none: bool = True) -> dict[str, Any]:
    logger.debug(f"Transfer schema to dict {schema=} {exclude_none=}")
    data = asdict(schema)
    if exclude_none:
        return {key: value for key, value in data.items() if value is not None}

    return data


def handle_unique_violation(func):

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            logger.exception(e)
            searched = re.search(r"\((.*)\)=\(.*\)", e.args[0])
            if not searched:
                raise e

            field_name = searched.group(1)
            exception = {
                'username': UserWithThisUsernameAlreadyExists,
                'phone': UserWithThisPhoneAlreadyExists,
                'email': UserWithThisEmailAlreadyExists,
            }[field_name]
            raise exception

    return wrapper


class Paginator(Generic[T, K]):

    def __init__(self, session: AsyncSession,
                 data_schema: Type[K],
                 count_query: Select[tuple[int]],
                 data_query: Select[tuple[T]]):
        self._session = session
        self._data_schema = data_schema
        self._count_query = count_query
        self._data_query = data_query

    async def _get_count(self) -> int:
        logger.debug("Fetching count for paginating data")
        result = await self._session.execute(self._count_query)
        count = result.scalar_one()
        logger.debug(f"Fetched count for paginating data: {count}")
        return count

    async def _get_data(self, offset: int, per_page: int):
        logger.debug(f"Fetching data for paginating data: {offset=} {per_page=}")
        result = await self._session.execute(
            self._data_query.offset(offset).limit(per_page)
        )
        data = result.fetchall()
        return data if data else []

    async def page(self, page: int, per_page: int) -> PaginatedData[K]:
        logger.debug(f"Fetching paginated data {page=} {per_page=}")
        data_count = await self._get_count()
        num_pages = math.ceil(data_count / per_page) or 1
        page = page if 0 < page <= num_pages else 1
        offset = (page - 1) * per_page
        data = await self._get_data(offset, per_page)
        data_schemas = [
            self._data_schema.model_validate(user[0]) for user in data
        ]
        logger.debug(f"Paginated data: {page=} {num_pages=} {per_page=} on_page_count={len(data_schemas)}")
        return PaginatedData(
            page=page, num_pages=num_pages, per_page=per_page,
            data=data_schemas
        )
