from dataclasses import asdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, or_, Select, func

from .graphql.graph_types import AuthData
from .schemas import DbUser
from .models import User
from .exceptions import UserDoesNotExist
from .utils import (
    handle_unique_violation,
    Paginator,
    PaginatedData,
)


class UsersQueries:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def _get_user_by_stmt(self, stmt: Select[tuple[User]]) -> DbUser:
        result = await self._session.execute(stmt)
        db_users = result.fetchone()
        if not db_users:
            raise UserDoesNotExist

        return DbUser.model_validate(db_users[0])

    async def get_by_phone_or_username(
            self,
            phone_or_username: str
    ) -> DbUser:
        stmt = select(User).where(or_(User.phone == phone_or_username,
                                      User.username == phone_or_username))
        return await self._get_user_by_stmt(stmt)

    async def get_by_id(self, id: int) -> DbUser:
        stmt = select(User).where(User.id == id)
        return await self._get_user_by_stmt(stmt)

    async def get_by_username(self, username: str) -> DbUser:
        stmt = select(User).where(User.username == username)
        return await self._get_user_by_stmt(stmt)

    async def get_by_email(self, email: str) -> DbUser:
        stmt = select(User).where(User.email == email)
        return await self._get_user_by_stmt(stmt)

    async def get_by_phone(self, phone: str) -> DbUser:
        stmt = select(User).where(User.phone == phone)
        return await self._get_user_by_stmt(stmt)

    @handle_unique_violation
    async def create(self, user_data: AuthData, password: str) -> DbUser:
        values = asdict(user_data)
        values['password'] = password
        del values['password_repeat']
        stmt = insert(User).returning(User).values(**values)
        result = await self._session.execute(stmt)
        return DbUser.model_validate(result.fetchone()[0])

    def _get_user_name_filters(self, query: str):
        filters = []
        for query_item in query.split(' '):
            filters.append(User.first_name.ilike(f"%{query_item}%"))
            filters.append(User.last_name.ilike(f"%{query_item}%"))
            filters.append(User.middle_name.ilike(f"%{query_item}%"))

        return filters

    def _get_search_count_stmt(self, query: str) -> Select[tuple[int]]:
        user_name_filters = self._get_user_name_filters(query)
        return select(func.count('*')).select_from(User).where(or_(
            *user_name_filters,
            User.username.ilike(f"%{query}%"),
        ))

    def _get_search_data_stmt(self, query: str) -> Select[tuple[User]]:
        user_name_filters = self._get_user_name_filters(query)
        return select(User).where(or_(
            *user_name_filters,
            User.username.ilike(f"%{query}%"),
        ))

    async def search(self,
                     query: str,
                     page: int,
                     per_page: int) -> PaginatedData[DbUser]:
        count_stmt = self._get_search_count_stmt(query)
        data_stmt = self._get_search_data_stmt(query)
        paginator = Paginator(self._session, DbUser,
                              count_stmt, data_stmt)
        return await paginator.page(page, per_page)
