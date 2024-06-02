from datetime import datetime

from pydantic import BaseModel


class SystemEvent(BaseModel):
    included_users: list[int]
    event_type: str
    data: str


class EventSavedFile(BaseModel):
    original_url: str
    original_filename: str
    converted_url: str | None = None
    converted_filename: str | None = None


class EventPermissionCategory(BaseModel):
    code: str
    name: str


class EventPermission(BaseModel):
    code: str
    name: str
    category: EventPermissionCategory | None = None


class EventUser(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email_confirmed: bool
    phone_confirmed: bool
    last_seen: datetime | None
    middle_name: str | None = None
    avatar: EventSavedFile | None = None
    phone: str | None = None
    email: str | None = None
    status: str | None = None
    permissions: list[EventPermission] | None = None
