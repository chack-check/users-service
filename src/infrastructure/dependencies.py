from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from domain.files.ports import FilesPort
from domain.notifications.handlers import SendVerificationCodeHandler, VerifyCodeHandler
from domain.notifications.ports import CodesStoragePort, NotificationSenderPort
from domain.sessions.handlers import (
    AuthenticateHandler,
    GenerateAuthSessionHandler,
    LoginHandler,
    LogoutAllHandler,
    LogoutHandler,
    RefreshSessionHandler,
    ValidateTokenHandler,
)
from domain.sessions.ports import SessionsStoragePort, TokensPort
from domain.users.handlers import (
    GetUserByRefreshTokenHandler,
    GetUserByTokenHandler,
    GetUserHandler,
    GetUsersByIdsHandler,
    ResetPasswordHandler,
    UpdateAvatarHandler,
    UpdateEmailHandler,
    UpdatePasswordHandler,
    UpdatePhoneHandler,
    UpdateUserHandler,
)
from domain.users.ports import UserEventsPort, UsersPort
from infrastructure.api.adapters import TokensAdapter, TokensLoggingAdapter
from infrastructure.database.adapters import (
    FilesAdapter,
    FilesLoggingAdapter,
    UsersAdapter,
    UsersLoggingAdapter,
)
from infrastructure.database.base import session
from infrastructure.memory_storage.adapters import (
    CodesStorageAdapter,
    CodesStorageLoggingAdapter,
    SessionsStorageAdapter,
    SessionsStorageLoggingAdapter,
)
from infrastructure.memory_storage.base import redis_db
from infrastructure.rabbit_publisher.adapters import (
    UserEventsAdapter,
    UserEventsLoggingAdapter,
)
from infrastructure.rabbit_publisher.publisher import connection


async def use_session() -> AsyncGenerator[AsyncSession, None]:
    async with session() as s:
        yield s
        await s.commit()


def use_users_adapter(session: AsyncSession) -> UsersPort:
    return UsersLoggingAdapter(UsersAdapter(session))


def use_tokens_adapter() -> TokensPort:
    return TokensLoggingAdapter(TokensAdapter())


def use_codes_storage_adapter() -> CodesStoragePort:
    return CodesStorageLoggingAdapter(CodesStorageAdapter(redis_db))


def use_sessions_storage_adapter() -> SessionsStoragePort:
    return SessionsStorageLoggingAdapter(SessionsStorageAdapter(redis_db))


def use_files_adapter(session: AsyncSession) -> FilesPort:
    return FilesLoggingAdapter(FilesAdapter(session))


def use_user_events_adapter() -> UserEventsPort:
    return UserEventsLoggingAdapter(UserEventsAdapter(connection))


def use_get_users_by_ids_handler(users_port: UsersPort, files_port: FilesPort) -> GetUsersByIdsHandler:
    return GetUsersByIdsHandler(users_port, files_port)


def use_get_user_handler(
    users_port: UsersPort,
    files_port: FilesPort,
) -> GetUserHandler:
    return GetUserHandler(users_port, files_port)


def use_login_handler(
    sessions_storage_port: SessionsStoragePort,
    users_port: UsersPort,
    tokens_port: TokensPort,
) -> LoginHandler:
    return LoginHandler(sessions_storage_port, tokens_port, users_port)


def use_logout_handler(
    sessions_storage_port: SessionsStoragePort,
    tokens_port: TokensPort,
    users_port: UsersPort,
) -> LogoutHandler:
    return LogoutHandler(sessions_storage_port, tokens_port, users_port)


def use_logout_all_handler(
    sessions_storage_port: SessionsStoragePort,
    tokens_port: TokensPort,
    users_port: UsersPort,
) -> LogoutAllHandler:
    return LogoutAllHandler(sessions_storage_port, tokens_port, users_port)


def use_validate_token_handler(tokens_port: TokensPort) -> ValidateTokenHandler:
    return ValidateTokenHandler(tokens_port)


def use_authenticate_handler(
    sessions_storage_port: SessionsStoragePort,
    users_port: UsersPort,
    tokens_port: TokensPort,
    files_port: FilesPort,
    user_events_port: UserEventsPort,
) -> AuthenticateHandler:
    return AuthenticateHandler(sessions_storage_port, tokens_port, users_port, files_port, user_events_port)


def use_send_verification_code_handler(
    sender: NotificationSenderPort,
    users_port: UsersPort,
    codes_storage_port: CodesStoragePort,
) -> SendVerificationCodeHandler:
    return SendVerificationCodeHandler(sender, users_port, codes_storage_port)


def use_verify_code_handler(codes_storage_port: CodesStoragePort) -> VerifyCodeHandler:
    return VerifyCodeHandler(codes_storage_port)


def use_get_user_by_token_handler(
    users_port: UsersPort,
    tokens_port: TokensPort,
    files_port: FilesPort,
) -> GetUserByTokenHandler:
    return GetUserByTokenHandler(users_port, tokens_port, files_port)


def use_get_user_by_refresh_token_handler(
    users_port: UsersPort,
    tokens_port: TokensPort,
    sessions_storage_port: SessionsStoragePort,
    files_port: FilesPort,
) -> GetUserByRefreshTokenHandler:
    return GetUserByRefreshTokenHandler(users_port, tokens_port, sessions_storage_port, files_port)


def use_update_me_handler(
    users_port: UsersPort,
    tokens_port: TokensPort,
    user_events_port: UserEventsPort,
    files_port: FilesPort,
) -> UpdateUserHandler:
    return UpdateUserHandler(users_port, tokens_port, user_events_port, files_port)


def use_update_avatar_handler(
    users_port: UsersPort,
    tokens_port: TokensPort,
    user_events_port: UserEventsPort,
    files_port: FilesPort,
) -> UpdateAvatarHandler:
    return UpdateAvatarHandler(users_port, tokens_port, files_port, user_events_port)


def use_refresh_handler(
    sessions_storage_port: SessionsStoragePort,
    users_port: UsersPort,
    tokens_port: TokensPort,
) -> RefreshSessionHandler:
    return RefreshSessionHandler(users_port, sessions_storage_port, tokens_port)


def use_update_password_handler(
    users_port: UsersPort,
    tokens_port: TokensPort,
    files_port: FilesPort,
) -> UpdatePasswordHandler:
    return UpdatePasswordHandler(users_port, tokens_port, files_port)


def use_update_email_handler(
    sessions_storage_port: SessionsStoragePort,
    users_port: UsersPort,
    tokens_port: TokensPort,
    user_events_port: UserEventsPort,
    files_port: FilesPort,
) -> UpdateEmailHandler:
    return UpdateEmailHandler(users_port, tokens_port, user_events_port, sessions_storage_port, files_port)


def use_update_phone_handler(
    sessions_storage_port: SessionsStoragePort,
    users_port: UsersPort,
    tokens_port: TokensPort,
    user_events_port: UserEventsPort,
    files_port: FilesPort,
) -> UpdatePhoneHandler:
    return UpdatePhoneHandler(
        users_port,
        tokens_port,
        user_events_port,
        sessions_storage_port,
        files_port,
    )


def use_reset_password_handler(
    sessions_storage_port: SessionsStoragePort,
    users_port: UsersPort,
    tokens_port: TokensPort,
) -> ResetPasswordHandler:
    return ResetPasswordHandler(
        users_port,
        tokens_port,
        sessions_storage_port,
    )


def use_generate_auth_session_handler(
    sessions_storage_port: SessionsStoragePort,
) -> GenerateAuthSessionHandler:
    return GenerateAuthSessionHandler(sessions_storage_port)
