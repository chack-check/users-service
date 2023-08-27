from typing import Literal

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from ..crud import UsersQueries
from ..exceptions import (
    PasswordsNotMatch,
    IncorrectPassword,
    IncorrectToken,
    UserDoesNotExist,
)
from ..schemas import (
    DbUser,
    UserUpdateData,
    UserAuthData,
    UserLoginData,
    UserCredentials,
)
from ..utils import (
    PaginatedData,
)
from .tokens import TokensSet
from .sessions import SessionSet


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UsersSet:

    def __init__(self, session: AsyncSession, redis_db: Redis):
        self._redis_db = redis_db
        self._users_queries = UsersQueries(session)
        self._tokens_set = TokensSet()
        self._sessions_set = SessionSet(redis_db)

    async def get(self, *, id: int | None = None,
                  username: str | None = None,
                  email: str | None = None,
                  phone: str | None = None) -> DbUser:
        assert any((id, username, email, phone)), "Specify get field"
        assert len(list(filter(bool, (id, username, email, phone)))) == 1, (
            "You can specify only one get field"
        )
        if id:
            user = await self._users_queries.get_by_id(id)
        elif username:
            user = await self._users_queries.get_by_username(username)
        elif email:
            user = await self._users_queries.get_by_email(email)
        elif phone:
            user = await self._users_queries.get_by_phone(phone)
        else:
            raise ValueError("You need to specify one field"
                             " value: id|username|email|phone")

        return user

    async def get_from_token(self, token: str, *,
                             raise_exception: bool = True) -> DbUser | None:
        try:
            user_id = self._tokens_set.decode_token(token)
            return await self._users_queries.get_by_id(user_id)
        except (IncorrectToken, UserDoesNotExist):
            if raise_exception:
                raise

            return None

    async def get_from_refresh_token(
            self, token: str, *,
            raise_exception: bool = True
    ) -> DbUser | None:
        try:
            user_id = self._tokens_set.decode_token(token)
            has_session = await self._sessions_set.has_user_session(
                user_id, token
            )
            if not has_session:
                raise UserDoesNotExist

            return await self._users_queries.get_by_id(user_id)
        except UserDoesNotExist:
            if raise_exception:
                raise

            return None

    async def search(self, *, query: str, page: int = 1,
                     per_page: int = 20) -> PaginatedData[DbUser]:
        paginated_users = await self._users_queries.search(
            query, page, per_page
        )
        return paginated_users

    async def get_by_ids(self, ids: list[int]) -> list[DbUser]:
        return await self._users_queries.get_by_ids(ids)

    def _verify_password(self, password: str, hash_: str) -> None:
        if not pwd_context.verify(password, hash_):
            raise IncorrectPassword

    async def login(self, login_data: UserLoginData) -> UserCredentials:
        db_user = await self._users_queries.get_by_phone_or_username(
            login_data.phone_or_username
        )
        self._verify_password(login_data.password, db_user.password)
        access_token = self._tokens_set.create_token(db_user, mode='access')
        refresh_token = self._tokens_set.create_token(db_user, mode='refresh')
        await self._sessions_set.create(db_user.id, refresh_token)
        return UserCredentials(
            access_token=access_token,
            refresh_token=refresh_token,
            user=db_user,
        )

    def _validate_passwords(self, password1: str, password2: str):
        if password1 != password2:
            raise PasswordsNotMatch('Passwords do not match')

    async def authenticate(
            self,
            auth_data: UserAuthData,
    ) -> UserCredentials:
        self._validate_passwords(auth_data.password, auth_data.password_repeat)
        password_hash = pwd_context.hash(auth_data.password)
        db_user = await self._users_queries.create(
            auth_data, password=password_hash
        )
        access_token = self._tokens_set.create_token(db_user, mode='access')
        refresh_token = self._tokens_set.create_token(db_user, mode='refresh')
        await self._sessions_set.create(db_user.id, refresh_token)
        return UserCredentials(
            access_token=access_token,
            refresh_token=refresh_token,
            user=db_user,
        )

    async def confirm_field(self, user: DbUser,
                            field: Literal['email', 'phone']):
        field_confirmed = getattr(user, f"{field}_confirmed")
        if field_confirmed:
            return

        method = {
            'email': self._users_queries.confirm_email,
            'phone': self._users_queries.confirm_phone,
        }[field]
        await method(user)

    async def update(self, user: DbUser,
                     update_data: UserUpdateData) -> DbUser:
        db_user = await self._users_queries.update(user, update_data)
        return db_user

    async def refresh(self, user: DbUser,
                      refresh_token: str) -> UserCredentials:
        has_session = await self._sessions_set.has_user_session(
            user.id, refresh_token
        )
        if not has_session:
            raise IncorrectToken

        new_access_token = self._tokens_set.create_token(user, mode='access')
        return UserCredentials(
            access_token=new_access_token,
            refresh_token=refresh_token,
            user=user,
        )

    async def logout_all(self, user_id: int):
        ...
