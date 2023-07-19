import math
from typing import TypeVar, Generic, NamedTuple, Type
import re
from dataclasses import fields

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Select

from .exceptions import (
    AuthRequired,
    UserWithThisEmailAlreadyExists,
    UserWithThisPhoneAlreadyExists,
    UserWithThisUsernameAlreadyExists,
)
from .schemas import DbUser


T = TypeVar('T')

K = TypeVar('K', bound=BaseModel)


class PaginatedData(NamedTuple, Generic[K]):
    page: int
    num_pages: int
    per_page: int
    data: list[K]


def validate_user_required(user: DbUser | None) -> None:
    if not user:
        raise AuthRequired()


def get_schema_from_pydantic(schema, model: BaseModel):
    include_fields = {field.name for field in fields(schema)}
    return schema(**model.model_dump(include=include_fields))


def handle_unique_violation(func):

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            field_name = re.search(r"\((.*)\)=\(.*\)", e.args[0]).group(1)
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
