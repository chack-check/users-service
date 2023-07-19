from typing import TypeAlias
import strawberry
from strawberry.types import Info

from ..services.users import UsersSet
from ..dependencies import CustomContext
from ..utils import validate_user_required, get_schema_from_pydantic
from .graph_types import (
    User, PaginatedUsersResponse, LoginData, Tokens,
    AuthData, UpdateData, ChangePasswordData,
    ChangeEmailData
)


CustomInfo: TypeAlias = Info[CustomContext, None]


@strawberry.type
class Query:

    @strawberry.field
    async def user_me(self, info: CustomInfo) -> User:
        validate_user_required(info.context.user)
        return get_schema_from_pydantic(User, info.context.user)

    @strawberry.field
    async def user(self, info: CustomInfo,
                   id: int | None = None,
                   username: str | None = None,
                   email: str | None = None) -> User:
        validate_user_required(info.context.user)
        return await info.context.users_set.get(
            id=id, username=username, email=email
        )

    @strawberry.field
    async def users(self,
                    info: CustomInfo,
                    query: str = '',
                    page: int = 1,
                    per_page: int = 20) -> PaginatedUsersResponse:
        validate_user_required(info.context.user)
        return await info.context.users_set.search(
            query=query, page=page, per_page=per_page
        )


@strawberry.type
class Mutation:

    @strawberry.mutation
    async def login(info: CustomInfo, login_data: LoginData) -> Tokens:
        users_set: UsersSet = info.context.users_set
        tokens = await users_set.login(login_data)
        return tokens

    @strawberry.mutation
    async def authenticate(info: CustomInfo, auth_data: AuthData) -> Tokens:
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
