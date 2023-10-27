import math
from typing import TypeVar, Generic, NamedTuple, Type, Any
import re
from dataclasses import fields, asdict

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Select

from app.v1.graphql.graph_types import AuthData

from .exceptions import (
    AuthRequired,
    UserWithThisEmailAlreadyExists,
    UserWithThisPhoneAlreadyExists,
    UserWithThisUsernameAlreadyExists,
    AuthenticationEmailOrPhoneRequired,
)
from .schemas import DbUser


T = TypeVar('T')

K = TypeVar('K', bound=BaseModel)


class PaginatedData(NamedTuple, Generic[K]):
    page: int
    num_pages: int
    per_page: int
    data: list[K]


def validate_auth_data(data: AuthData) -> None:
    if not data.email and not data.phone:
        raise AuthenticationEmailOrPhoneRequired


def validate_user_required(user: DbUser | None) -> None:
    if not user:
        raise AuthRequired()


def get_schema_from_pydantic(schema, model: K):
    include_fields = {field.name for field in fields(schema)}
    return schema(**model.model_dump(include=include_fields))


def get_pydantic_from_schema(schema, model: Type[K]) -> K:
    return model.model_validate(asdict(schema))


def to_dict(schema, *, exclude_none: bool = True) -> dict[str, Any]:
    data = asdict(schema)
    if exclude_none:
        return {key: value for key, value in data.items() if value is not None}

    return data


def handle_unique_violation(func):

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
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
        result = await self._session.execute(self._count_query)
        count = result.fetchone()[0]
        return count

    async def _get_data(self, offset: int, per_page: int):
        result = await self._session.execute(
            self._data_query.offset(offset).limit(per_page)
        )
        data = result.fetchall()
        return data if data else []

    async def page(self, page: int, per_page: int) -> PaginatedData[K]:
        data_count = await self._get_count()
        num_pages = math.ceil(data_count / per_page) or 1
        page = page if 0 < page <= num_pages else 1
        offset = (page - 1) * per_page
        data = await self._get_data(offset, per_page)
        data_schemas = [
            self._data_schema.model_validate(user[0]) for user in data
        ]
        return PaginatedData(
            page=page, num_pages=num_pages, per_page=per_page,
            data=data_schemas
        )
