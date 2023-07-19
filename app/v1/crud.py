import math
from dataclasses import asdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, or_, Select, func

from .graphql.graph_types import AuthData
from .schemas import DbUser
from .models import User
from .exceptions import UserDoesNotExist
from .utils import handle_unique_violation


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

    async def _get_users_count(self, query: str) -> int:
        user_name_filters = self._get_user_name_filters(query)
        stmt = select(func.count('*')).select_from(User).where(or_(
            *user_name_filters,
            User.username.ilike(f"%{query}%"),
        ))
        result = await self._session.execute(stmt)
        count = result.fetchone()[0]
        return count

    async def _search_users(self,
                            query: str,
                            offset: int,
                            per_page: int) -> list[User]:
        user_name_filters = self._get_user_name_filters(query)
        stmt = select(User).where(or_(
            *user_name_filters,
            User.username.ilike(f"%{query}%"),
        )).offset(offset).limit(per_page)
        result = await self._session.execute(stmt)
        users = result.fetchall()
        return users if users else []

    async def search(self,
                     query: str,
                     page: int,
                     per_page: int) -> tuple[list[DbUser], int, int]:
        users_count = await self._get_users_count(query)
        num_pages = math.ceil(users_count / per_page) or 1
        page = page if 0 < page <= num_pages else 1
        offset = (page - 1) * per_page
        users = await self._search_users(query, offset, per_page)
        db_users = [DbUser.model_validate(user[0]) for user in users]
        return db_users, page, num_pages
