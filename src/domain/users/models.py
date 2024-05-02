import re
from datetime import datetime

from email_validator import EmailNotValidError, validate_email
from passlib.context import CryptContext

from domain.files.models import SavedFile
from domain.permissions.models import Permission

from .exceptions import IncorrectEmail, IncorrectPhoneNumber

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

PHONE_PATTERN = r"^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$"


class User:
    _id: int
    _username: str
    _password: str
    _first_name: str
    _last_name: str
    _email_confirmed: bool
    _phone_confirmed: bool
    _last_seen: datetime
    _middle_name: str | None
    _avatar: SavedFile | None
    _phone: str | None
    _email: str | None
    _status: str | None
    _permissions: list[Permission]

    def __init__(
        self,
        id_: int,
        username: str,
        password: str,
        first_name: str,
        last_name: str,
        email_confirmed: bool,
        phone_confirmed: bool,
        last_seen: datetime,
        middle_name: str | None = None,
        avatar: SavedFile | None = None,
        phone: str | None = None,
        email: str | None = None,
        status: str | None = None,
        permissions: list[Permission] | None = None,
    ) -> None:
        self._id = id_
        self._username = username
        self._password = password
        self._first_name = first_name
        self._last_name = last_name
        self._email_confirmed = email_confirmed
        self._phone_confirmed = phone_confirmed
        self._last_seen = last_seen
        self._middle_name = middle_name
        self._avatar = avatar
        self._phone = phone
        self._email = email
        self._status = status
        self._permissions = permissions if permissions else []

    def get_id(self) -> int:
        return self._id

    def get_username(self) -> str:
        return self._username

    def get_password(self) -> str:
        return self._password

    def set_password(self, password: str, hashed: bool = False):
        if hashed:
            self._password = password

        self._password = password_context.hash(password)

    def validate_password(self, password: str) -> bool:
        return password_context.verify(password, self._password)

    def get_first_name(self) -> str:
        return self._first_name

    def set_first_name(self, first_name: str) -> None:
        self._first_name = first_name

    def get_last_name(self) -> str:
        return self._last_name

    def set_last_name(self, last_name: str) -> None:
        self._last_name = last_name

    def get_email_confirmed(self) -> bool:
        return self._email_confirmed

    def confirm_email(self) -> None:
        self._email_confirmed = True

    def confirm_phone(self) -> None:
        self._phone_confirmed = True

    def get_phone_confirmed(self) -> bool:
        return self._phone_confirmed

    def get_last_seen(self) -> datetime:
        return self._last_seen

    def get_middle_name(self) -> str | None:
        return self._middle_name

    def set_middle_name(self, middle_name: str) -> None:
        self._middle_name = middle_name

    def get_full_name(self) -> str:
        if self._middle_name:
            return f"{self._last_name} {self._first_name} {self._middle_name}"

        return f"{self._last_name} {self._first_name}"

    def get_avatar(self) -> SavedFile | None:
        return self._avatar

    def set_avatar(self, file: SavedFile) -> None:
        self._avatar = file

    def get_phone(self) -> str | None:
        return self._phone

    def set_phone(self, phone: str) -> None:
        if not re.match(PHONE_PATTERN, phone):
            raise IncorrectPhoneNumber("incorrect phone number")

        self._phone = phone

    def get_email(self) -> str | None:
        return self._email

    def set_email(self, email: str) -> None:
        try:
            validate_email(email)
        except EmailNotValidError:
            raise IncorrectEmail("incorrect email")

        self._email = email

    def get_status(self) -> str | None:
        return self._status

    def set_status(self, status: str) -> None:
        self._status = status

    def get_permissions(self) -> list[Permission]:
        return self._permissions

    def add_permission(self, permission: Permission) -> None:
        if permission in self._permissions:
            return

        self._permissions.append(permission)

    def set_permissions(self, permissions: list[Permission]) -> None:
        self._permissions = permissions

    def remove_permission(self, permission: Permission) -> None:
        if permission not in self._permissions:
            return

        self._permissions.remove(permission)

    def has_permission(self, permission: Permission) -> bool:
        return permission in self._permissions

    def __repr__(self) -> str:
        data = {
            "id": self._id,
            "username": self._username,
            "first_name": self._first_name,
            "last_name": self._last_name,
            "email_confirmed": self._email_confirmed,
            "phone_confirmed": self._phone_confirmed,
            "last_seen": self._last_seen,
            "middle_name": self._middle_name,
            "avatar": self._avatar,
            "phone": self._phone,
            "email": self._email,
            "status": self._status,
            "permissions": self._permissions,
        }
        return f"{self.__class__.__name__}{data}"


class UpdateData:
    _first_name: str | None
    _last_name: str | None
    _middle_name: str | None
    _status: str | None

    def __init__(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
        middle_name: str | None = None,
        status: str | None = None,
    ):
        self._first_name = first_name
        self._last_name = last_name
        self._middle_name = middle_name
        self._status = status

    def get_first_name(self) -> str | None:
        return self._first_name

    def get_last_name(self) -> str | None:
        return self._last_name

    def get_middle_name(self) -> str | None:
        return self._middle_name

    def get_status(self) -> str | None:
        return self._status

    def __repr__(self) -> str:
        data = {
            "first_name": self._first_name,
            "last_name": self._last_name,
            "middle_name": self._middle_name,
            "status": self._status,
        }
        return f"{self.__class__.__name__}{data}"
