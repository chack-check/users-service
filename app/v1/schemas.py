from datetime import datetime
from enum import Enum

from pydantic import AwareDatetime, BaseModel, ConfigDict, EmailStr


class UserActivities(str, Enum):
    online = 'online'
    offline = 'offline'
    call = 'call'
    away = 'away'


class SavingFileSystemFiletypes(Enum):
    avatar = 'avatar'
    file_in_chat = 'file_in_chat'


class UserCredentials(BaseModel):
    access_token: str
    refresh_token: str
    user: "DbUser"


class SavedFile(BaseModel):
    original_url: str
    original_filename: str
    converted_url: str | None = None
    converted_filename: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BaseUser(BaseModel):
    email: EmailStr | None = None
    username: str
    avatar: SavedFile | None = None
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


class UserPatchData(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    phone: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    password: str | None = None
    activity: UserActivities | None = None
    status: str | None = None
    last_seen: AwareDatetime | None = None
    email_confirmed: bool | None = None
    phone_confirmed: bool | None = None


class UserLoginData(BaseModel):
    phone_or_username: str
    password: str


class SavingFileObject(BaseModel):
    filename: str
    url: str
    signature: str
    system_filetype: SavingFileSystemFiletypes


class SavingFileData(BaseModel):
    original_file: SavingFileObject
    converted_file: SavingFileObject | None = None


class UserAuthData(BaseUser):
    password: str
    password_repeat: str
    avatar_file: SavingFileData | None = None


class FileUrl(BaseModel):
    filename: str
    url: str


class AuthenticationSession(BaseModel):
    session: str
    exp: datetime


class UserEvent(BaseModel):
    event_type: str
    included_users: list[int]
    data: str
