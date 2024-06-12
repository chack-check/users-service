import hashlib
import hmac
import math
from logging import getLogger
from urllib.parse import urljoin

from sqlalchemy import ColumnElement, Select, delete, insert, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import ReturningUpdate
from sqlalchemy.sql.functions import concat, count

from domain.files.models import SavedFile, UploadingFile, UploadingFileMeta
from domain.files.ports import FilesPort
from domain.general.models import PaginatedResponse
from domain.permissions.models import Permission
from domain.users.exceptions import UserAlreadyExists
from domain.users.models import User
from domain.users.ports import UsersPort
from infrastructure.database.exceptions import IncorrectFileSignature
from infrastructure.settings import settings

from .factories import SavedFileFactory, UserFactory
from .models import Permission as PermissionModel
from .models import User as UserModel
from .models import UserAvatar, user_permission

logger = getLogger("uvicorn.error")


class UsersLoggingAdapter(UsersPort):

    def __init__(self, adapter: UsersPort):
        self._adapter = adapter

    async def get_by_phone_or_username(self, phone_or_username: str) -> User | None:
        logger.debug(f"fetching user by: {phone_or_username=}")
        try:
            user = await self._adapter.get_by_phone_or_username(phone_or_username)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"fetched user: {user=}")
        return user

    async def get_by_email_or_phone(self, email_or_phone: str) -> User | None:
        logger.debug(f"fetching user by: {email_or_phone=}")
        try:
            user = await self._adapter.get_by_email_or_phone(email_or_phone)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"fetched user: {user=}")
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        logger.debug(f"fetching user by: {user_id=}")
        try:
            user = await self._adapter.get_by_id(user_id)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"fetched user: {user=}")
        return user

    async def get_by_username(self, username: str) -> User | None:
        logger.debug(f"fetching user by: {username=}")
        try:
            user = await self._adapter.get_by_username(username)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"fetched user: {user=}")
        return user

    async def get_by_email(self, email: str) -> User | None:
        logger.debug(f"fetching user by: {email=}")
        try:
            user = await self._adapter.get_by_email(email)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"fetched user: {user=}")
        return user

    async def get_by_ids(self, ids: list[int]) -> list[User]:
        logger.debug(f"fetching users by ids: {ids=}")
        try:
            users = await self._adapter.get_by_ids(ids)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"fetched users: {users=}")
        return users

    async def get_by_phone(self, phone: str) -> User | None:
        logger.debug(f"fetching user by: {phone=}")
        try:
            user = await self._adapter.get_by_phone(phone)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"fetched user: {user=}")
        return user

    async def save(self, user: User) -> User:
        logger.debug(f"saving user: {user=}")
        try:
            saved_user = await self._adapter.save(user)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"saved user: {saved_user=}")
        return saved_user

    async def search_users(self, query: str, page: int = 1, per_page: int = 100) -> PaginatedResponse[User]:
        logger.debug(f"searching users: {query=} {page=} {per_page=}")
        try:
            users = await self._adapter.search_users(query, page, per_page)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"founded users length: {len(users.get_data())}")
        return users


class UsersAdapter(UsersPort):

    def __init__(self, session: AsyncSession):
        self._session = session
        self._default_page = 1
        self._default_per_page = 100

    async def _get_user_by_stmt(
        self, stmt: Select[tuple[UserModel]] | ReturningUpdate[tuple[UserModel]]
    ) -> User | None:
        result = await self._session.execute(stmt)
        db_user = result.scalar_one_or_none()
        return UserFactory.domain_from_orm(db_user) if db_user else None

    async def get_by_phone_or_username(self, phone_or_username: str) -> User | None:
        stmt = select(UserModel).where(
            or_(UserModel.phone == phone_or_username, UserModel.username == phone_or_username)
        )
        return await self._get_user_by_stmt(stmt)

    async def get_by_email_or_phone(self, email_or_phone: str) -> User | None:
        stmt = select(UserModel).where(or_(UserModel.phone == email_or_phone, UserModel.email == email_or_phone))
        return await self._get_user_by_stmt(stmt)

    async def get_by_id(self, user_id: int) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        return await self._get_user_by_stmt(stmt)

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(UserModel).where(UserModel.username == username)
        return await self._get_user_by_stmt(stmt)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        return await self._get_user_by_stmt(stmt)

    async def get_by_ids(self, ids: list[int]) -> list[User]:
        stmt = select(UserModel).where(UserModel.id.in_(ids))
        result = await self._session.execute(stmt)
        db_users = result.scalars().all()
        return [UserFactory.domain_from_orm(u) for u in db_users]

    async def get_by_phone(self, phone: str) -> User | None:
        stmt = select(UserModel).where(UserModel.phone == phone)
        return await self._get_user_by_stmt(stmt)

    async def _save_avatar(self, avatar: SavedFile) -> int:
        avatar_dict = SavedFileFactory.dict_from_domain(avatar)
        stmt = insert(UserAvatar).returning(UserAvatar.id).values(**avatar_dict)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def _update_user_permissions(self, user_id: int, permissions: list[Permission]):
        stmt = delete(user_permission).where(user_permission.c.user_id == user_id)
        await self._session.execute(stmt)
        permission_ids_result = await self._session.execute(
            select(PermissionModel.id).where(PermissionModel.code.in_([p.get_code() for p in permissions]))
        )
        permission_ids = permission_ids_result.scalars().all()
        permission_params = [{"user_id": user_id, "permission_id": p_id} for p_id in permission_ids]
        if permission_params:
            await self._session.execute(insert(user_permission), permission_params)

    async def _get_or_save_avatar(self, avatar: SavedFile | None) -> int | None:
        if avatar and not avatar.get_id():
            saved_avatar_id = await self._save_avatar(avatar)
        elif avatar and avatar.get_id():
            saved_avatar_id = avatar.get_id()
        else:
            saved_avatar_id = None

        return saved_avatar_id

    async def _create_or_update_user(self, user: User, saved_avatar_id: int | None) -> int:
        stmt_data = UserFactory.dict_from_domain(user, saved_avatar_id)
        if user.get_id():
            stmt = update(UserModel).returning(UserModel.id).where(UserModel.id == user.get_id()).values(**stmt_data)
        else:
            stmt = insert(UserModel).returning(UserModel.id).values(stmt_data)

        try:
            result = await self._session.execute(stmt)
        except IntegrityError:
            raise UserAlreadyExists(f"user with these credentials already exists")

        saved_user_id = result.scalar_one()
        return saved_user_id

    async def save(self, user: User) -> User:
        avatar = user.get_avatar()
        saved_avatar_id = await self._get_or_save_avatar(avatar)
        saved_user_id = await self._create_or_update_user(user, saved_avatar_id)
        await self._update_user_permissions(saved_user_id, user.get_permissions())
        saved_user = await self._get_user_by_stmt(select(UserModel).where(UserModel.id == saved_user_id))
        assert saved_user, "error saving user"
        return saved_user

    async def _get_count_for_query(self, whereclause: ColumnElement[bool]) -> int:
        count_stmt = select(count()).select_from(UserModel).where(whereclause)
        count_result = await self._session.execute(count_stmt)
        count_scalar = count_result.scalar_one()
        return count_scalar

    async def _get_pagination_result(
        self, whereclause: ColumnElement[bool], offset: int, limit: int
    ) -> list[UserModel]:
        result_stmt = select(UserModel).where(whereclause).offset(offset).limit(limit)
        print(result_stmt.compile(compile_kwargs={"literal_binds": True}))
        result = await self._session.execute(result_stmt)
        result_users = result.scalars().all()
        return list(result_users)

    async def _paginate_query(
        self, whereclause: ColumnElement[bool], page: int = 1, per_page: int = 100
    ) -> PaginatedResponse[User]:
        per_page = per_page or self._default_per_page
        page = page or self._default_page
        count_value = await self._get_count_for_query(whereclause)
        pages_count = math.ceil(count_value / per_page)
        if page > pages_count:
            page = self._default_page

        result_users = await self._get_pagination_result(whereclause, (page - 1) * per_page, per_page)
        users_models = [UserFactory.domain_from_orm(user) for user in result_users]
        return PaginatedResponse(
            page,
            per_page,
            pages_count,
            count_value,
            users_models,
        )

    async def search_users(self, query: str, page: int = 1, per_page: int = 100) -> PaginatedResponse[User]:
        whereclause = or_(
            UserModel.username.icontains(query),
            concat(UserModel.first_name, " ", UserModel.last_name, " ", UserModel.middle_name).icontains(query),
        )
        result_users = await self._paginate_query(whereclause, page, per_page)
        return result_users


class FilesLoggingAdapter(FilesPort):

    def __init__(self, adapter: FilesPort):
        self._adapter = adapter

    async def save(self, file: SavedFile) -> SavedFile:
        logger.debug(f"saving file: {file=}")
        try:
            saved_file = await self._adapter.save(file)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"saved file: {saved_file=}")
        return saved_file

    def validate_uploading(self, file: UploadingFile) -> None:
        logger.debug(f"validating file: {file=}")
        try:
            self._adapter.validate_uploading(file)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"file validated: {file=}")

    def get_default(self, user: User) -> SavedFile:
        logger.debug(f"fetching default avatar for user: {user=}")
        try:
            default_file = self._adapter.get_default(user)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"fetched default avatar: {default_file=}")
        return default_file


class FilesAdapter(FilesPort):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, file: SavedFile) -> SavedFile:
        file_dict = SavedFileFactory.dict_from_domain(file)
        if file.get_id():
            stmt = update(UserAvatar).returning(UserAvatar).where(UserAvatar.id == file.get_id()).values(**file_dict)
        else:
            stmt = insert(UserAvatar).returning(UserAvatar).values(**file_dict)

        result = await self._session.execute(stmt)
        saved_file = result.scalar_one()
        return SavedFileFactory.domain_from_orm(saved_file)

    def _validate_file_meta(self, meta: UploadingFileMeta) -> None:
        file_signature = hmac.new(
            settings.files_signature_secret.encode(),
            (f"{meta.get_filename()}:{meta.get_system_filetype().value}").encode(),
            hashlib.sha256,
        ).hexdigest()
        if not file_signature == meta.get_signature():
            raise IncorrectFileSignature("incorrect signature")

    def validate_uploading(self, file: UploadingFile) -> None:
        self._validate_file_meta(file.get_original())
        if converted := file.get_converted():
            self._validate_file_meta(converted)

    def get_default(self, user: User) -> SavedFile:
        default_url = urljoin(settings.avatar_service_url, f"?squares=8&size=128&word={user.get_username()}")
        default_filename = f"{user.get_username()}.svg"
        return SavedFile(
            id_=0,
            original_url=default_url,
            original_filename=default_filename,
        )
