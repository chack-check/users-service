from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class UserResponse(_message.Message):
    __slots__ = ("id", "username", "phone", "email", "first_name", "last_name", "middle_name", "activity", "status", "email_confirmed", "phone_confirmed", "last_seen", "original_avatar_url", "converted_avatar_url")
    ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    MIDDLE_NAME_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    EMAIL_CONFIRMED_FIELD_NUMBER: _ClassVar[int]
    PHONE_CONFIRMED_FIELD_NUMBER: _ClassVar[int]
    LAST_SEEN_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_AVATAR_URL_FIELD_NUMBER: _ClassVar[int]
    CONVERTED_AVATAR_URL_FIELD_NUMBER: _ClassVar[int]
    id: int
    username: str
    phone: str
    email: str
    first_name: str
    last_name: str
    middle_name: str
    activity: str
    status: str
    email_confirmed: bool
    phone_confirmed: bool
    last_seen: str
    original_avatar_url: str
    converted_avatar_url: str
    def __init__(self, id: _Optional[int] = ..., username: _Optional[str] = ..., phone: _Optional[str] = ..., email: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., middle_name: _Optional[str] = ..., activity: _Optional[str] = ..., status: _Optional[str] = ..., email_confirmed: bool = ..., phone_confirmed: bool = ..., last_seen: _Optional[str] = ..., original_avatar_url: _Optional[str] = ..., converted_avatar_url: _Optional[str] = ...) -> None: ...

class GetUserByIdRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class GetUserByUsernameRequest(_message.Message):
    __slots__ = ("username",)
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    def __init__(self, username: _Optional[str] = ...) -> None: ...

class GetUserByEmailRequest(_message.Message):
    __slots__ = ("email",)
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    email: str
    def __init__(self, email: _Optional[str] = ...) -> None: ...

class GetUserByTokenRequest(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...
