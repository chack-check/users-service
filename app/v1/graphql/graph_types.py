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


@strawberry.enum
class VerificationSources(Enum):
    email = 'email'
    phone = 'phone'


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
    avatar_url: str | None = None


@strawberry.type
class VerificationSended:
    sended: bool


@strawberry.input
class AuthData:
    username: str
    first_name: str
    last_name: str
    password: str
    password_repeat: str
    middle_name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None


@strawberry.input
class UpdateData:
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    status: str | None = None
    avatar_url: str | None = None


@strawberry.input
class LoginData:
    phone_or_username: str
    password: str


@strawberry.type
class AuthSessionResponse:
    session: str
    exp: datetime


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
    old_email: EmailStr
    new_email: EmailStr
    session: str


@strawberry.input
class ChangePhoneData:
    old_phone: str
    new_phone: str
    session: str
