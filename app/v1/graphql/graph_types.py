from datetime import datetime
from enum import Enum

import strawberry
import email_validator


EmailStr = strawberry.scalar(
    str,
    serialize=lambda v: email_validator.validate_email(v).normalized,
    parse_value=lambda v: email_validator.validate_email(v).normalized,
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
    phone: str
    email: str
    first_name: str
    last_name: str
    middle_name: str | None = None
    activity: UserActivities
    status: str | None = None
    email_confirmed: bool
    phone_confirmed: bool
    last_seen: datetime


@strawberry.input
class AuthData:
    email: EmailStr
    username: str
    phone: str
    first_name: str
    last_name: str
    middle_name: str | None = None
    password: str
    password_repeat: str


@strawberry.input
class UpdateData:
    first_name: str
    last_name: str
    middle_name: str | None = None
    status: str | None = None


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
