from typing import Any, Literal

from sqlalchemy import Select, func, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import ReturningUpdate

from .exceptions import UserDoesNotExist
from .models import User, UserAvatar
from .schemas import DbUser, SavingFileData, UserAuthData, UserPatchData, UserUpdateData
from .utils import PaginatedData, Paginator, handle_unique_violation


class UsersQueries:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def _get_user_by_stmt(self, stmt: Select[tuple[User]] | ReturningUpdate[tuple[User]]) -> DbUser:
        result = await self._session.execute(stmt)
        db_user = result.scalar_one_or_none()
        if not db_user:
            raise UserDoesNotExist

        return DbUser.model_validate(db_user)

    async def get_by_phone_or_username(
            self,
            phone_or_username: str
    ) -> DbUser:
        stmt = select(User).where(
            or_(User.phone == phone_or_username, User.username == phone_or_username)
        )
        return await self._get_user_by_stmt(stmt)

    async def get_by_email_or_phone(
            self, email_or_phone: str
    ) -> DbUser:
        stmt = select(User).where(or_(User.phone == email_or_phone,
                                      User.email == email_or_phone))
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

    async def get_by_ids(self, ids: list[int]) -> list[DbUser]:
        stmt = select(User).where(User.id.in_(ids))
        result = await self._session.execute(stmt)
        db_users = result.fetchall()
        return [DbUser.model_validate(user[0]) for user in db_users]

    async def get_by_phone(self, phone: str) -> DbUser:
        stmt = select(User).where(User.phone == phone)
        return await self._get_user_by_stmt(stmt)

    def _get_creation_data(
            self,
            user_data: UserAuthData,
            password: str,
            avatar_id: int | None = None,
            field_confirmed: Literal['email', 'phone'] | None = None
    ) -> dict[str, Any]:
        values = user_data.model_dump(exclude={"avatar_file", "avatar"})
        values['password'] = password
        if field_confirmed:
            values[f"{field_confirmed}_confirmed"] = True

        if avatar_id:
            values["avatar_id"] = avatar_id

        del values['password_repeat']
        return values

    async def save_avatar_file(self, file_data: SavingFileData) -> int:
        avatar_values = {
            "original_url": file_data.original_file.url,
            "original_filename": file_data.original_file.filename,
            "converted_url": file_data.converted_file.url if file_data.converted_file else None,
            "converted_filename": file_data.converted_file.filename if file_data.converted_file else None,
        }
        stmt = insert(UserAvatar).returning(UserAvatar.id).values(**avatar_values)
        result = await self._session.execute(stmt)
        result_id = result.scalar_one()
        return result_id

    @handle_unique_violation
    async def create(
            self, user_data: UserAuthData, password: str,
            avatar_id: int | None = None,
            field_confirmed: Literal['email', 'phone'] | None = None
    ) -> DbUser:
        values = self._get_creation_data(
            user_data, password, avatar_id, field_confirmed
        )
        stmt = insert(User).returning(User).values(**values)
        result = await self._session.execute(stmt)
        result_user = result.scalar_one_or_none()
        if not result_user:
            raise ValueError(f"There is no created user: {result_user=}")

        return DbUser.model_validate(result_user)

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

    async def update(self, user: DbUser,
                     update_data: UserUpdateData) -> DbUser:
        clear_data = update_data.model_dump(exclude_none=True)
        if not clear_data:
            return user

        stmt = update(User).returning(User).values(
            **clear_data
        ).where(User.id == user.id)
        return await self._get_user_by_stmt(stmt)

    async def patch(self, user: DbUser, data: UserPatchData) -> DbUser:
        clear_data = data.model_dump(exclude_none=True)
        if not clear_data:
            return user

        stmt = update(User).returning(User).values(
            **clear_data
        ).where(User.id == user.id)
        return await self._get_user_by_stmt(stmt)

    async def confirm_email(self, user: DbUser):
        stmt = update(User).values(
            email_confirmed=True
        ).where(User.id == user.id)
        await self._session.execute(stmt)

    async def confirm_phone(self, user: DbUser):
        stmt = update(User).values(
            phone_confirmed=True
        ).where(User.id == user.id)
        await self._session.execute(stmt)
