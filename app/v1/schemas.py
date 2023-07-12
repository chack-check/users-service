from enum import Enum

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


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
    last_seen: datetime

    model_config = ConfigDict(from_attributes=True)


class UserOut(BaseUser):
    id: int
    activity: UserActivities
    status: str | None = None
    last_seen: datetime
