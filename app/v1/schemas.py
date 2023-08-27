from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    AwareDatetime,
)


class UserActivities(str, Enum):
    online = 'online'
    offline = 'offline'
    call = 'call'
    away = 'away'


class UserCredentials(BaseModel):
    access_token: str
    refresh_token: str
    user: "DbUser"


class BaseUser(BaseModel):
    email: EmailStr | None = None
    username: str
    phone: str | None = None
    first_name: str
    last_name: str
    middle_name: str | None = None


class DbUser(BaseUser):
    password: str
    id: int
    activity: UserActivities
    status: str | None = None
    last_seen: AwareDatetime
    email_confirmed: bool = False
    phone_confirmed: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserUpdateData(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    status: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserLoginData(BaseModel):
    phone_or_username: str
    password: str


class UserAuthData(BaseUser):
    password: str
    password_repeat: str
