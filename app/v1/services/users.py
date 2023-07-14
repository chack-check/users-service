from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from ..graphql.graph_types import (
    User, PaginatedUsersResponse, LoginData,
    Tokens, AuthData, UpdateData
)
from ..crud import UsersQueries
from ..exceptions import PasswordsNotMatch
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
                  email: str | None = None) -> User:
        ...

    async def all(self, *, query: str, page: int = 1,
                  per_page: int = 20) -> PaginatedUsersResponse:
        ...

    async def login(self, login_data: LoginData) -> Tokens:
        ...

    def _validate_passwords(self, password1: str, password2: str):
        if password1 != password2:
            raise PasswordsNotMatch('Passwords do not match')

    async def authenticate(self, auth_data: AuthData) -> Tokens:
        self._validate_passwords(auth_data.password, auth_data.password_repeat)
        password_hash = pwd_context.hash(auth_data.password)
        db_user = await self._users_queries.create(auth_data,
                                                   password=password_hash)
        access_token = self._tokens_set.create_token(db_user, mode='access')
        refresh_token = self._tokens_set.create_token(db_user, mode='refresh')
        await self._sessions_set.create(db_user.id, refresh_token)
        return Tokens(access_token=access_token, refresh_token=refresh_token)

    async def update(self, update_data: UpdateData) -> User:
        ...

    async def logout(self, user_id: int):
        ...

    async def refresh(self, user_id: int, refresh_token: str) -> Tokens:
        ...

    async def logout_all(self, user_id: int):
        ...
