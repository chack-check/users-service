import logging
from typing import Any, Literal

from sqlalchemy import Select, delete, func, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import ReturningUpdate

from .exceptions import UserDoesNotExist
from .models import User, UserAvatar, user_permission
from .schemas import (
    DbUser,
    PermissionDto,
    SavingFileData,
    UserAuthData,
    UserPatchData,
    UserUpdateData,
)
from .utils import PaginatedData, Paginator, handle_unique_violation

logger = logging.getLogger("uvicorn.error")


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
        logger.debug(f"Fetching user by phone or username: {phone_or_username}")
        stmt = select(User).where(
            or_(User.phone == phone_or_username, User.username == phone_or_username)
        )
        return await self._get_user_by_stmt(stmt)

    async def get_by_email_or_phone(
            self, email_or_phone: str
    ) -> DbUser:
        logger.debug(f"Fetching user by email or phone: {email_or_phone}")
        stmt = select(User).where(or_(User.phone == email_or_phone,
                                      User.email == email_or_phone))
        return await self._get_user_by_stmt(stmt)

    async def get_by_id(self, id: int) -> DbUser:
        logger.debug(f"Fetching user by id: {id}")
        stmt = select(User).where(User.id == id)
        return await self._get_user_by_stmt(stmt)

    async def get_by_username(self, username: str) -> DbUser:
        logger.debug(f"Fetching user by username: {username}")
        stmt = select(User).where(User.username == username)
        return await self._get_user_by_stmt(stmt)

    async def get_by_email(self, email: str) -> DbUser:
        logger.debug(f"Fetching user by email: {email}")
        stmt = select(User).where(User.email == email)
        return await self._get_user_by_stmt(stmt)

    async def get_by_ids(self, ids: list[int]) -> list[DbUser]:
        logger.debug(f"Fetching users by ids: {ids}")
        stmt = select(User).where(User.id.in_(ids))
        result = await self._session.execute(stmt)
        db_users = result.fetchall()
        logger.debug(f"Fetched users by ids count: {len(db_users)}")
        return [DbUser.model_validate(user[0]) for user in db_users]

    async def get_by_phone(self, phone: str) -> DbUser:
        logger.debug(f"Fetching user by phone: {phone}")
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
        logger.debug(f"Saving avatar file: {file_data}")
        avatar_values = {
            "original_url": file_data.original_file.url,
            "original_filename": file_data.original_file.filename,
            "converted_url": file_data.converted_file.url if file_data.converted_file else None,
            "converted_filename": file_data.converted_file.filename if file_data.converted_file else None,
        }
        logger.debug(f"Saving avatar file dict: {avatar_values}")
        stmt = insert(UserAvatar).returning(UserAvatar.id).values(**avatar_values)
        result = await self._session.execute(stmt)
        result_id = result.scalar_one()
        logger.debug(f"Saved avatar id: {result_id}")
        return result_id

    @handle_unique_violation
    async def create(
            self, user_data: UserAuthData, password: str,
            avatar_id: int | None = None,
            field_confirmed: Literal['email', 'phone'] | None = None
    ) -> DbUser:
        logger.debug(f"Creating user: {user_data=} {avatar_id=} {field_confirmed=}")
        values = self._get_creation_data(
            user_data, password, avatar_id, field_confirmed
        )
        stmt = insert(User).returning(User).values(**values)
        result = await self._session.execute(stmt)
        result_user = result.scalar_one_or_none()
        logger.debug(f"Created user: {result_user=}")
        if not result_user:
            logger.error(f"Not created user: {result_user=}")
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
        logger.debug(f"Updating user: {user=} {update_data=}")
        clear_data = update_data.model_dump(exclude_none=True)
        logger.debug(f"Cleared update user data: {clear_data}")
        if not clear_data:
            logger.debug("Cleared update user data is empty. Skip")
            return user

        stmt = update(User).returning(User).values(
            **clear_data
        ).where(User.id == user.id)
        return await self._get_user_by_stmt(stmt)

    async def patch(self, user: DbUser, data: UserPatchData) -> DbUser:
        logger.debug(f"Patching user: {user=} {data=}")
        clear_data = data.model_dump(exclude_none=True)
        logger.debug(f"Cleared patch user data: {clear_data}")
        if not clear_data:
            logger.debug("Cleared patch user data is empty. Skip")
            return user

        stmt = update(User).returning(User).values(
            **clear_data
        ).where(User.id == user.id)
        return await self._get_user_by_stmt(stmt)

    async def confirm_email(self, user: DbUser):
        logger.debug(f"Confirming email for user: {user=}")
        stmt = update(User).values(
            email_confirmed=True
        ).where(User.id == user.id)
        await self._session.execute(stmt)

    async def confirm_phone(self, user: DbUser):
        logger.debug(f"Confirming phone for user: {user=}")
        stmt = update(User).values(
            phone_confirmed=True
        ).where(User.id == user.id)
        await self._session.execute(stmt)

    async def _save_user_avatar(self, db_user: DbUser, new_avatar: SavingFileData) -> None:
        stmt = insert(UserAvatar).values(
            original_url=new_avatar.original_file.url,
            original_filename=new_avatar.original_file.filename,
            converted_url=new_avatar.converted_file.url if new_avatar.converted_file else None,
            converted_filename=new_avatar.converted_file.filename if new_avatar.converted_file else None,
        ).returning(UserAvatar.id)
        result = await self._session.execute(stmt)
        avatar_id = result.scalar_one()
        stmt = update(User).values(avatar_id=avatar_id).where(User.id == db_user.id)
        await self._session.execute(stmt)

    async def _update_user_avatar(self, db_user: DbUser, new_avatar: SavingFileData) -> None:
        stmt = update(UserAvatar).values(
            original_url=new_avatar.original_file.url,
            original_filename=new_avatar.original_file.filename,
            converted_url=new_avatar.converted_file.url if new_avatar.converted_file else None,
            converted_filename=new_avatar.converted_file.filename if new_avatar.converted_file else None,
        ).where(UserAvatar.users.any(User.id == db_user.id))
        await self._session.execute(stmt)

    async def _clear_user_avatar(self, db_user: DbUser) -> None:
        update_user_avatar_id_stmt = update(User).values(avatar_id=None).where(User.id == db_user.id)
        await self._session.execute(update_user_avatar_id_stmt)
        stmt = delete(UserAvatar).where(UserAvatar.users.any(User.id == db_user.id))
        await self._session.execute(stmt)

    async def update_avatar(self, db_user: DbUser, new_avatar: SavingFileData | None = None) -> None:
        logger.debug(f"Updating user avatar {db_user=} {new_avatar=}")
        if not db_user.avatar and new_avatar:
            logger.debug("User avatar is empty and new avatar is not empty. Creating new avatar for user")
            await self._save_user_avatar(db_user, new_avatar)
        elif new_avatar:
            logger.debug("User avatar is not empty and new avatar is not empty. Updating user avatar")
            await self._update_user_avatar(db_user, new_avatar)
        else:
            logger.debug("New user avatar is empty. Clear user avatars")
            await self._clear_user_avatar(db_user)

    async def set_permissions(self, db_user: DbUser, new_permissions: list[PermissionDto]) -> DbUser:
        logger.debug(f"Clearing user permissions {db_user=}")
        stmt = delete(user_permission).where(user_permission.c.user_id == db_user.id)
        await self._session.execute(stmt)
        if new_permissions:
            logger.debug(f"Setting user permissions {db_user=} {new_permissions=}")
            stmt = insert(user_permission).values(
                [{"user_id": db_user.id, "permission_id": perm.id} for perm in new_permissions]
            )
            await self._session.execute(stmt)

        stmt = select(User).where(User.id == db_user.id)
        result = await self._session.execute(stmt)
        updated_user = result.scalar_one()
        logger.debug(f"User permissions updated {updated_user=}")
        return DbUser.model_validate(updated_user)
