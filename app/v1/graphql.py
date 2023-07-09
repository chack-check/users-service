from enum import Enum

import strawberry
from strawberry.types import Info
import email_validator


EmailStr = strawberry.scalar(
    str,
    serialize=lambda v: email_validator.validate_email,
    parse_value=email_validator.validate_email,
)


@strawberry.enum
class UserActivities(Enum):
    online = 'online'
    offline = 'offline'
    call = 'call'
    away = 'away'


@strawberry.type
class User:
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    middle_name: str | None = None
    activity: UserActivities
    status: str | None = None


@strawberry.input
class AuthData:
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: str | None = None


@strawberry.input
class UpdateData:
    first_name: str
    last_name: str
    middle_name: str | None = None


@strawberry.input
class LoginData:
    email: EmailStr
    password: str


@strawberry.type
class Tokens:
    access_token: str
    refresh_token: str


@strawberry.type
class PaginatedUsersResponse:
    page: int
    num_pages: int
    per_page: int
    data: list[User]


@strawberry.input
class ChangePasswordData:
    old_password: str
    new_password: str


@strawberry.input
class ChangeEmailData:
    email: EmailStr


@strawberry.type
class Query:

    @strawberry.field
    async def user_me(self) -> User:
        return User(id=1, username='username', email='email', first_name='ivan', last_name='ivanov', activity='online')

    @strawberry.field
    async def user(self, id: int | None = None, username: str | None = None, email: str | None = None) -> User:
        ...

    @strawberry.field
    async def users(self, query: str = '', page: int = 1, per_page: int = 20) -> PaginatedUsersResponse:
        ...


@strawberry.type
class Mutation:

    @strawberry.mutation
    async def login(login_data: LoginData) -> Tokens:
        ...

    @strawberry.mutation
    async def authenticate(auth_data: AuthData) -> Tokens:
        ...

    @strawberry.mutation
    async def update(update_data: UpdateData) -> User:
        ...

    @strawberry.mutation
    async def refresh() -> Tokens:
        ...

    @strawberry.mutation
    async def update_password(change_password_data: ChangePasswordData) -> User:
        ...
    
    @strawberry.mutation
    async def update_email(change_email_data: ChangeEmailData) -> User:
        ...
