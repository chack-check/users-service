from datetime import datetime
from typing import Literal

from sqlalchemy.exc import IntegrityError

from domain.files.models import SavedFile
from domain.files.ports import FilesPort
from domain.sessions.exceptions import (
    IncorrectAuthData,
    IncorrectTokenException,
    NoSessionsToRefreshException,
)
from domain.sessions.models import (
    AuthData,
    AuthenticationSession,
    AuthSessionOperations,
    LoginData,
    Session,
    TokenPairData,
)
from domain.sessions.ports import SessionsStoragePort, TokensPort
from domain.users.exceptions import UserAlreadyExists, UserNotFound
from domain.users.models import User
from domain.users.ports import UserEventsPort, UsersPort


class RefreshSessionHandler:

    def __init__(
        self, users_port: UsersPort, sessions_storage_port: SessionsStoragePort, tokens_port: TokensPort
    ) -> None:
        self._sessions_storage_port = sessions_storage_port
        self._tokens_port = tokens_port
        self._users_port = users_port

    async def execute(self, refresh_token: str) -> TokenPairData:
        user_id = await self._tokens_port.decode_token(refresh_token)
        if not user_id:
            raise IncorrectTokenException("incorrect token")

        user = await self._users_port.get_by_id(user_id)
        if not user:
            raise IncorrectTokenException("incorrect token")

        session = Session(refresh_token, user)
        if not await self._sessions_storage_port.has_session(session):
            raise NoSessionsToRefreshException("there are no sessions to refresh")

        new_access_token = self._tokens_port.create_token(user, "access")
        return TokenPairData(refresh_token, new_access_token, user)


class LoginHandler:

    def __init__(self, sessions_storage_port: SessionsStoragePort, tokens_port: TokensPort, users_port: UsersPort):
        self._sessions_storage_port = sessions_storage_port
        self._tokens_port = tokens_port
        self._users_port = users_port

    async def execute(self, login_data: LoginData) -> TokenPairData:
        user = await self._users_port.get_by_phone_or_username(login_data.get_phone_or_username())
        if not user:
            raise UserNotFound("user not found")

        if not user.validate_password(login_data.get_password()):
            raise UserNotFound("user not found")

        access_token = self._tokens_port.create_token(user, "access")
        refresh_token = self._tokens_port.create_token(user, "refresh")
        session = Session(refresh_token, user)
        await self._sessions_storage_port.save(session)
        return TokenPairData(refresh_token, access_token, user)


class AuthenticateHandler:

    def __init__(
        self,
        sessions_storage_port: SessionsStoragePort,
        tokens_port: TokensPort,
        users_port: UsersPort,
        files_port: FilesPort,
        user_events_port: UserEventsPort,
    ):
        self._sessions_storage_port = sessions_storage_port
        self._tokens_port = tokens_port
        self._users_port = users_port
        self._files_port = files_port
        self._user_events_port = user_events_port

    async def execute(
        self,
        auth_session: str,
        verification_source: Literal["email", "phone"],
        auth_data: AuthData,
    ) -> TokenPairData:
        if not auth_data.get_email() and not auth_data.get_phone():
            raise IncorrectAuthData("you need to specify email or phone")

        field = auth_data.get_email() if verification_source == "email" else auth_data.get_phone()
        if not field:
            raise IncorrectAuthData("you need to specify phone or email")

        await self._sessions_storage_port.verify_auth_session(field, AuthSessionOperations.authentication, auth_session)
        if file := auth_data.get_avatar():
            self._files_port.validate_uploading(file)
            if file_meta := file.get_converted():
                converted_url = file_meta.get_url()
                converted_filename = file_meta.get_filename()
            else:
                converted_url, converted_filename = None, None

            file_to_save = SavedFile(
                id_=0,
                original_url=file.get_original().get_url(),
                original_filename=file.get_original().get_filename(),
                converted_url=converted_url,
                converted_filename=converted_filename,
            )
            saved_avatar = await self._files_port.save(file_to_save)
        else:
            saved_avatar = None

        user = User(
            id_=0,
            username=auth_data.get_username(),
            email=auth_data.get_email(),
            phone=auth_data.get_phone(),
            password=auth_data.get_password_hash(),
            first_name=auth_data.get_first_name(),
            last_name=auth_data.get_last_name(),
            middle_name=auth_data.get_middle_name(),
            email_confirmed=verification_source == "email",
            phone_confirmed=verification_source == "phone",
            last_seen=datetime.now(),
            avatar=saved_avatar,
        )
        saved_user = await self._users_port.save(user)
        access_token = self._tokens_port.create_token(saved_user, "access")
        refresh_token = self._tokens_port.create_token(saved_user, "refresh")
        session = Session(refresh_token, user)
        await self._sessions_storage_port.save(session)
        await self._user_events_port.send_user_created(saved_user)
        return TokenPairData(refresh_token, access_token, saved_user)


class GenerateAuthSessionHandler:

    def __init__(
        self,
        sessions_storage_port: SessionsStoragePort,
    ):
        self._sessions_storage_port = sessions_storage_port

    async def execute(self, email_or_phone: str, operation: AuthSessionOperations) -> AuthenticationSession:
        session = await self._sessions_storage_port.generate_auth_session(email_or_phone, operation)
        return session


class LogoutHandler:

    def __init__(self, sessions_storage_port: SessionsStoragePort, tokens_port: TokensPort, users_port: UsersPort):
        self._sessions_storage_port = sessions_storage_port
        self._tokens_port = tokens_port
        self._users_port = users_port

    async def execute(self, token: str) -> None:
        user_id = await self._tokens_port.decode_token(token)
        if user_id == 0:
            raise IncorrectTokenException("Incorrect token")

        user = await self._users_port.get_by_id(user_id)
        if not user:
            raise IncorrectTokenException("Incorrect token")

        session = Session(token, user)
        await self._sessions_storage_port.delete(session)


class LogoutAllHandler:

    def __init__(self, sessions_storage_port: SessionsStoragePort, tokens_port: TokensPort, users_port: UsersPort):
        self._sessions_storage_port = sessions_storage_port
        self._tokens_port = tokens_port
        self._users_port = users_port

    async def execute(self, token: str) -> None:
        user_id = await self._tokens_port.decode_token(token)
        if user_id == 0:
            raise IncorrectTokenException("Incorrect token")

        user = await self._users_port.get_by_id(user_id)
        if not user:
            raise IncorrectTokenException("Incorrect token")

        await self._sessions_storage_port.delete_all(user)


class ValidateTokenHandler:

    def __init__(self, tokens_port: TokensPort):
        self._tokens_port = tokens_port

    async def execute(self, token: str) -> bool:
        user_id = await self._tokens_port.decode_token(token)
        return user_id != 0
