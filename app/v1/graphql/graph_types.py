from datetime import datetime
from enum import Enum

import email_validator
import strawberry

from ..constants import UserPermissionsEnum

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


UserPermissionsCodes = strawberry.enum(UserPermissionsEnum)


@strawberry.enum
class VerificationSources(Enum):
    email = 'email'
    phone = 'phone'


@strawberry.enum
class SystemFiletypes(Enum):
    avatar = 'avatar'
    file_in_chat = 'file_in_chat'


@strawberry.input
class UploadFileObject:
    url: str
    signature: str
    filename: str
    system_filetype: SystemFiletypes


@strawberry.input
class UploadFileData:
    original_file: UploadFileObject
    converted_file: UploadFileObject | None = None


@strawberry.type
class UploadedFile:
    original_url: str
    original_filename: str
    converted_url: str | None = None
    converted_filename: str | None = None


@strawberry.input
class CreatePermissionData:
    code: str
    name: str


@strawberry.input
class CreatePermissionCategoryData:
    code: str
    name: str


@strawberry.type
class PermissionCategory:
    code: str
    name: str


@strawberry.type
class Permission:
    code: str
    name: str
    category: PermissionCategory | None = None


@strawberry.type
class User:
    id: int
    username: str
    phone: str | None = None
    email: str | None = None
    first_name: str
    last_name: str
    middle_name: str | None = None
    activity: UserActivities
    status: str | None = None
    email_confirmed: bool
    phone_confirmed: bool
    last_seen: datetime
    avatar: UploadedFile | None = None
    permissions: list[Permission] = strawberry.field(default_factory=list)


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
    avatar_file: UploadFileData | None = None


@strawberry.input
class UpdateData:
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    status: str | None = None


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
