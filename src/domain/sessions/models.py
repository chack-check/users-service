from datetime import datetime
from enum import Enum

from passlib.context import CryptContext

from domain.files.models import UploadingFile
from domain.users.models import User

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthSessionOperations(Enum):
    authentication = "authentication"
    update_email = "update_email"
    update_phone = "update_phone"
    reset_password = "reset_password"


class Session:
    _refresh_token: str
    _user: User

    def __init__(self, refresh_token: str, user: User):
        self._refresh_token = refresh_token
        self._user = user

    def get_refresh_token(self) -> str:
        return self._refresh_token

    def get_user(self) -> User:
        return self._user

    def __repr__(self) -> str:
        data = {
            "refresh_token": self._refresh_token,
            "user": self._user,
        }
        return f"{self.__class__.__name__}{data}"


class TokenPairData:
    _refresh_token: str
    _access_token: str
    _user: User

    def __init__(self, refresh_token: str, access_token: str, user: User):
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._user = user

    def get_access_token(self) -> str:
        return self._access_token

    def get_refresh_token(self) -> str:
        return self._refresh_token

    def get_user(self) -> User:
        return self._user

    def __repr__(self) -> str:
        data = {
            "refresh_token": self._refresh_token,
            "access_token": self._refresh_token,
            "user": self._user,
        }
        return f"{self.__class__.__name__}{data}"


class AuthData:
    _username: str
    _password: str
    _first_name: str
    _last_name: str
    _middle_name: str | None = None
    _email: str | None = None
    _phone: str | None = None
    _avatar: UploadingFile | None = None

    def __init__(
        self,
        username: str,
        password: str,
        first_name: str,
        last_name: str,
        middle_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        avatar: UploadingFile | None = None,
    ):
        self._username = username
        self._password = password
        self._first_name = first_name
        self._last_name = last_name
        self._middle_name = middle_name
        self._email = email
        self._phone = phone
        self._avatar = avatar

    def get_username(self) -> str:
        return self._username

    def get_password(self) -> str:
        return self._password

    def get_password_hash(self) -> str:
        return password_context.hash(self._password)

    def get_first_name(self) -> str:
        return self._first_name

    def get_last_name(self) -> str:
        return self._last_name

    def get_middle_name(self) -> str | None:
        return self._middle_name

    def get_email(self) -> str | None:
        return self._email

    def get_phone(self) -> str | None:
        return self._phone

    def get_avatar(self) -> UploadingFile | None:
        return self._avatar

    def __repr__(self) -> str:
        data = {
            "username": self._username,
            "first_name": self._first_name,
            "last_name": self._last_name,
            "middle_name": self._middle_name,
            "email": self._email,
            "phone": self._phone,
            "avatar": self._avatar,
        }
        return f"{self.__class__.__name__}{data}"


class LoginData:
    _phone_or_username: str
    _password: str

    def __init__(self, phone_or_username: str, password: str):
        self._phone_or_username = phone_or_username
        self._password = password

    def get_phone_or_username(self) -> str:
        return self._phone_or_username

    def get_password(self) -> str:
        return self._password

    def __repr__(self) -> str:
        data = {
            "phone_or_username": self._phone_or_username,
        }
        return f"{self.__class__.__name__}{data}"


class AuthenticationSession:
    _session: str
    _exp: datetime

    def __init__(self, session: str, exp: datetime):
        self._session = session
        self._exp = exp

    def get_session(self) -> str:
        return self._session

    def get_exp(self) -> datetime:
        return self._exp

    def __repr__(self) -> str:
        data = {
            "session": self._session,
            "exp": self._exp,
        }
        return f"{self.__class__.__name__}{data}"
