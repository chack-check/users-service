import strawberry
from strawberry.types import Info

from ..services.users import UsersSet
from .graph_types import (
    User, PaginatedUsersResponse, LoginData, Tokens,
    AuthData, UpdateData, ChangePasswordData,
    ChangeEmailData
)


@strawberry.type
class Query:

    @strawberry.field
    async def user_me(self) -> User:
        ...

    @strawberry.field
    async def user(self, id: int | None = None, username: str | None = None,
                   email: str | None = None) -> User:
        ...

    @strawberry.field
    async def users(self, query: str = '', page: int = 1,
                    per_page: int = 20) -> PaginatedUsersResponse:
        ...


@strawberry.type
class Mutation:

    @strawberry.mutation
    async def login(info: Info, login_data: LoginData) -> Tokens:
        users_set: UsersSet = info.context.users_set
        tokens = await users_set.login(login_data)
        return tokens

    @strawberry.mutation
    async def authenticate(info: Info, auth_data: AuthData) -> Tokens:
        users_set = info.context.users_set
        tokens = await users_set.authenticate(auth_data)
        return tokens

    @strawberry.mutation
    async def update(update_data: UpdateData) -> User:
        ...

    @strawberry.mutation
    async def refresh() -> Tokens:
        ...

    @strawberry.mutation
    async def update_password(
        change_password_data: ChangePasswordData
    ) -> User:
        ...

    @strawberry.mutation
    async def update_email(
        change_email_data: ChangeEmailData
    ) -> User:
        ...
