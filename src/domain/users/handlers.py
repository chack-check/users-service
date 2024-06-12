from typing import Literal

from domain.files.models import SavedFile, UploadingFile
from domain.files.ports import FilesPort
from domain.general.models import PaginatedResponse
from domain.sessions.exceptions import IncorrectTokenException
from domain.sessions.models import AuthSessionOperations, Session, TokenPairData
from domain.sessions.ports import SessionsStoragePort, TokensPort

from .exceptions import (
    IncorrectPasswordException,
    SearchUserIncorrectParameters,
    UserNotFound,
)
from .models import UpdateData, User
from .ports import UserEventsPort, UsersPort


class GetUserHandler:

    def __init__(self, users_port: UsersPort, files_port: FilesPort) -> None:
        self._users_port = users_port
        self._files_port = files_port

    async def execute(
        self, id_: int | None = None, username: str | None = None, email: str | None = None, phone: str | None = None
    ) -> User:
        if not any((id_, username, email, phone)):
            raise SearchUserIncorrectParameters("incorrect parameters: you need to specify id|username|email|phone")

        if id_:
            user = await self._users_port.get_by_id(id_)
        elif username:
            user = await self._users_port.get_by_username(username)
        elif email:
            user = await self._users_port.get_by_email(email)
        elif phone:
            user = await self._users_port.get_by_phone(phone)
        else:
            raise UserNotFound

        if not user:
            raise UserNotFound

        if not user.get_avatar():
            user.set_avatar(self._files_port.get_default(user))

        return user


class GetUserByTokenHandler:

    def __init__(self, users_port: UsersPort, tokens_port: TokensPort, files_port: FilesPort):
        self._users_port = users_port
        self._tokens_port = tokens_port
        self._files_port = files_port

    async def execute(self, token: str) -> User:
        user_id = await self._tokens_port.decode_token(token)
        if not user_id:
            raise IncorrectTokenException("incorrect token")

        user = await self._users_port.get_by_id(user_id)
        if not user:
            raise IncorrectTokenException("incorrect token")

        if not user.get_avatar():
            user.set_avatar(self._files_port.get_default(user))

        return user


class GetUserByRefreshTokenHandler:

    def __init__(
        self,
        users_port: UsersPort,
        tokens_port: TokensPort,
        sessions_storage_port: SessionsStoragePort,
        files_port: FilesPort,
    ):
        self._users_port = users_port
        self._sessions_storage_port = sessions_storage_port
        self._tokens_port = tokens_port
        self._files_port = files_port

    async def execute(self, token: str) -> User:
        user_id = await self._tokens_port.decode_token(token)
        if not user_id:
            raise IncorrectTokenException("incorrect token")

        user = await self._users_port.get_by_id(user_id)
        if not user:
            raise IncorrectTokenException("incorrect token")

        session = Session(token, user)
        if not await self._sessions_storage_port.has_session(session):
            raise IncorrectTokenException("Incorrect token")

        if not user.get_avatar():
            user.set_avatar(self._files_port.get_default(user))

        return user


class GetUsersByIdsHandler:

    def __init__(self, users_port: UsersPort, files_port: FilesPort) -> None:
        self._users_port = users_port
        self._files_port = files_port

    async def execute(self, ids: list[int]) -> list[User]:
        users = await self._users_port.get_by_ids(ids)
        for user in users:
            if not user.get_avatar():
                user.set_avatar(self._files_port.get_default(user))

        return users


class ConfirmFieldHandler:

    def __init__(self, users_port: UsersPort, files_port: FilesPort) -> None:
        self._users_port = users_port
        self._files_port = files_port

    async def execute(self, user_id: int, field: Literal["email", "phone"]) -> User:
        user = await self._users_port.get_by_id(user_id)
        if not user:
            raise UserNotFound

        if field == "email":
            user.confirm_email()
        else:
            user.confirm_phone()

        saved_user = await self._users_port.save(user)
        if not user.get_avatar():
            user.set_avatar(self._files_port.get_default(user))

        return saved_user


class UpdateUserHandler:

    def __init__(
        self, users_port: UsersPort, tokens_port: TokensPort, user_events_port: UserEventsPort, files_port: FilesPort
    ) -> None:
        self._users_port = users_port
        self._tokens_port = tokens_port
        self._user_events_port = user_events_port
        self._files_port = files_port

    async def execute(self, token: str, update_data: UpdateData) -> User:
        user_id = await self._tokens_port.decode_token(token)
        if not user_id:
            raise IncorrectTokenException("incorrect token")

        user = await self._users_port.get_by_id(user_id)
        if not user:
            raise IncorrectTokenException("incorrect token")

        if first_name := update_data.get_first_name():
            user.set_first_name(first_name)
        if last_name := update_data.get_last_name():
            user.set_last_name(last_name)
        if middle_name := update_data.get_middle_name():
            user.set_middle_name(middle_name)
        if status := update_data.get_status():
            user.set_status(status)

        saved_user = await self._users_port.save(user)
        await self._user_events_port.send_user_changed(saved_user)
        if not user.get_avatar():
            user.set_avatar(self._files_port.get_default(user))

        return saved_user


class UpdateAvatarHandler:

    def __init__(
        self, users_port: UsersPort, tokens_port: TokensPort, files_port: FilesPort, user_events_port: UserEventsPort
    ):
        self._users_port = users_port
        self._tokens_port = tokens_port
        self._files_port = files_port
        self._user_events_port = user_events_port

    async def execute(self, token: str, new_avatar: UploadingFile | None = None) -> User:
        user_id = await self._tokens_port.decode_token(token)
        if not user_id:
            raise IncorrectTokenException("incorrect token")

        user = await self._users_port.get_by_id(user_id)
        if not user:
            raise IncorrectTokenException("incorrect token")

        if not new_avatar:
            default_avatar = self._files_port.get_default(user)
            user.set_avatar(default_avatar)
        else:
            self._files_port.validate_uploading(new_avatar)
            if converted := new_avatar.get_converted():
                converted_url = converted.get_url()
                converted_filename = converted.get_filename()
            else:
                converted_url, converted_filename = None, None

            saved_file = SavedFile(
                id_=0,
                original_url=new_avatar.get_original().get_url(),
                original_filename=new_avatar.get_original().get_filename(),
                converted_url=converted_url,
                converted_filename=converted_filename,
            )
            user.set_avatar(saved_file)

        saved_user = await self._users_port.save(user)
        if not user.get_avatar():
            user.set_avatar(self._files_port.get_default(user))

        await self._user_events_port.send_user_changed(saved_user)
        return saved_user


class UpdatePasswordHandler:

    def __init__(self, users_port: UsersPort, tokens_port: TokensPort, files_port: FilesPort):
        self._users_port = users_port
        self._tokens_port = tokens_port
        self._files_port = files_port

    async def execute(self, token: str, old_password: str, new_password: str) -> User:
        user_id = await self._tokens_port.decode_token(token)
        if not user_id:
            raise IncorrectTokenException("incorrect token")

        user = await self._users_port.get_by_id(user_id)
        if not user:
            raise IncorrectTokenException("incorrect token")

        if not user.validate_password(old_password):
            raise IncorrectPasswordException("incorrect old password")

        user.set_password(new_password)
        saved_user = await self._users_port.save(user)
        if not user.get_avatar():
            user.set_avatar(self._files_port.get_default(user))

        return saved_user


class UpdateEmailHandler:

    def __init__(
        self,
        users_port: UsersPort,
        tokens_port: TokensPort,
        user_events_port: UserEventsPort,
        sessions_storage_port: SessionsStoragePort,
        files_port: FilesPort,
    ):
        self._users_port = users_port
        self._tokens_port = tokens_port
        self._user_events_port = user_events_port
        self._sessions_storage_port = sessions_storage_port
        self._files_port = files_port

    async def execute(self, token: str, auth_session: str, new_email: str) -> User:
        user_id = await self._tokens_port.decode_token(token)
        if not user_id:
            raise IncorrectTokenException("incorrect token")

        user = await self._users_port.get_by_id(user_id)
        if not user:
            raise IncorrectTokenException("incorrect token")

        await self._sessions_storage_port.verify_auth_session(
            new_email, AuthSessionOperations.update_email, auth_session
        )
        user.set_email(new_email)
        saved_user = await self._users_port.save(user)
        if not user.get_avatar():
            user.set_avatar(self._files_port.get_default(user))

        await self._user_events_port.send_user_changed(saved_user)
        return saved_user


class UpdatePhoneHandler:

    def __init__(
        self,
        users_port: UsersPort,
        tokens_port: TokensPort,
        user_events_port: UserEventsPort,
        sessions_storage_port: SessionsStoragePort,
        files_port: FilesPort,
    ):
        self._users_port = users_port
        self._tokens_port = tokens_port
        self._user_events_port = user_events_port
        self._sessions_storage_port = sessions_storage_port
        self._files_port = files_port

    async def execute(self, token: str, auth_session: str, new_phone: str) -> User:
        user_id = await self._tokens_port.decode_token(token)
        if not user_id:
            raise IncorrectTokenException("incorrect token")

        user = await self._users_port.get_by_id(user_id)
        if not user:
            raise IncorrectTokenException("incorrect token")

        await self._sessions_storage_port.verify_auth_session(
            new_phone, AuthSessionOperations.update_phone, auth_session
        )
        user.set_phone(new_phone)
        saved_user = await self._users_port.save(user)
        if not user.get_avatar():
            user.set_avatar(self._files_port.get_default(user))

        await self._user_events_port.send_user_changed(saved_user)
        return saved_user


class ResetPasswordHandler:

    def __init__(
        self,
        users_port: UsersPort,
        tokens_port: TokensPort,
        sessions_storage_port: SessionsStoragePort,
    ):
        self._users_port = users_port
        self._tokens_port = tokens_port
        self._sessions_storage_port = sessions_storage_port

    async def execute(self, auth_session: str, email_or_phone: str, new_password: str) -> TokenPairData:
        user = await self._users_port.get_by_email_or_phone(email_or_phone)
        if not user:
            raise UserNotFound("there is no such user")

        await self._sessions_storage_port.verify_auth_session(
            email_or_phone, AuthSessionOperations.reset_password, auth_session
        )
        user.set_password(new_password)
        saved_user = await self._users_port.save(user)
        await self._sessions_storage_port.delete_all(user)
        refresh_token = self._tokens_port.create_token(user, "refresh")
        access_token = self._tokens_port.create_token(user, "access")
        return TokenPairData(refresh_token, access_token, saved_user)


class SearchUsersHandler:

    def __init__(self, users_port: UsersPort, tokens_port: TokensPort):
        self._users_port = users_port
        self._tokens_port = tokens_port

    async def execute(self, query: str, page: int, per_page: int, token: str) -> PaginatedResponse[User]:
        user_id = await self._tokens_port.decode_token(token)
        if not user_id:
            raise IncorrectTokenException("incorrect token")

        user = await self._users_port.get_by_id(user_id)
        if not user:
            raise IncorrectTokenException("incorrect token")

        users = await self._users_port.search_users(query, page, per_page)
        return users
