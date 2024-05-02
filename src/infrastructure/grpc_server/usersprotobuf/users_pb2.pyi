from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SavedFile(_message.Message):
    __slots__ = ("original_url", "original_filename", "converted_url", "converted_filename")
    ORIGINAL_URL_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_FILENAME_FIELD_NUMBER: _ClassVar[int]
    CONVERTED_URL_FIELD_NUMBER: _ClassVar[int]
    CONVERTED_FILENAME_FIELD_NUMBER: _ClassVar[int]
    original_url: str
    original_filename: str
    converted_url: str
    converted_filename: str
    def __init__(self, original_url: _Optional[str] = ..., original_filename: _Optional[str] = ..., converted_url: _Optional[str] = ..., converted_filename: _Optional[str] = ...) -> None: ...

class UserResponse(_message.Message):
    __slots__ = ("id", "username", "phone", "email", "first_name", "last_name", "middle_name", "status", "email_confirmed", "phone_confirmed", "avatar")
    ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    MIDDLE_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    EMAIL_CONFIRMED_FIELD_NUMBER: _ClassVar[int]
    PHONE_CONFIRMED_FIELD_NUMBER: _ClassVar[int]
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    id: int
    username: str
    phone: str
    email: str
    first_name: str
    last_name: str
    middle_name: str
    status: str
    email_confirmed: bool
    phone_confirmed: bool
    avatar: SavedFile
    def __init__(self, id: _Optional[int] = ..., username: _Optional[str] = ..., phone: _Optional[str] = ..., email: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., middle_name: _Optional[str] = ..., status: _Optional[str] = ..., email_confirmed: bool = ..., phone_confirmed: bool = ..., avatar: _Optional[_Union[SavedFile, _Mapping]] = ...) -> None: ...

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

class GetUsersByIdsRequest(_message.Message):
    __slots__ = ("ids",)
    IDS_FIELD_NUMBER: _ClassVar[int]
    ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, ids: _Optional[_Iterable[int]] = ...) -> None: ...

class UsersArrayResponse(_message.Message):
    __slots__ = ("users",)
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[UserResponse]
    def __init__(self, users: _Optional[_Iterable[_Union[UserResponse, _Mapping]]] = ...) -> None: ...
