from enum import Enum

from datetime import datetime

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


class BaseUser(BaseModel):
    email: EmailStr
    username: str
    phone: str
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
