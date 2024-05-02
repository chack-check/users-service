from domain.files.ports import FilesPort
from domain.notifications.handlers import SendVerificationCodeHandler, VerifyCodeHandler
from domain.notifications.ports import CodesStoragePort, NotificationSenderPort
from domain.sessions.handlers import (
    AuthenticateHandler,
    GenerateAuthSessionHandler,
    LoginHandler,
    RefreshSessionHandler,
)
from domain.sessions.ports import SessionsStoragePort, TokensPort
from domain.users.handlers import (
    ConfirmFieldHandler,
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


def use_get_user_handler(users_port: UsersPort) -> GetUserHandler:
    return GetUserHandler(users_port)


def use_get_users_by_ids_handler(users_port: UsersPort) -> GetUsersByIdsHandler:
    return GetUsersByIdsHandler(users_port)


def use_confirm_field_handler(users_port: UsersPort) -> ConfirmFieldHandler:
    return ConfirmFieldHandler(users_port)


def use_update_user_handler(
    users_port: UsersPort, tokens_port: TokensPort, user_events_port: UserEventsPort
) -> UpdateUserHandler:
    return UpdateUserHandler(users_port, tokens_port, user_events_port)


def use_update_avatar_handler(
    users_port: UsersPort, tokens_port: TokensPort, files_port: FilesPort, user_events_port: UserEventsPort
) -> UpdateAvatarHandler:
    return UpdateAvatarHandler(users_port, tokens_port, files_port, user_events_port)


def use_update_password_handler(users_port: UsersPort, tokens_port: TokensPort) -> UpdatePasswordHandler:
    return UpdatePasswordHandler(users_port, tokens_port)


def use_update_email_handler(
    users_port: UsersPort,
    tokens_port: TokensPort,
    user_events_port: UserEventsPort,
    sessions_storage_port: SessionsStoragePort,
) -> UpdateEmailHandler:
    return UpdateEmailHandler(users_port, tokens_port, user_events_port, sessions_storage_port)


def use_update_phone_handler(
    users_port: UsersPort,
    tokens_port: TokensPort,
    user_events_port: UserEventsPort,
    sessions_storage_port: SessionsStoragePort,
) -> UpdatePhoneHandler:
    return UpdatePhoneHandler(users_port, tokens_port, user_events_port, sessions_storage_port)


def use_reset_password_handler(
    users_port: UsersPort, tokens_port: TokensPort, sessions_storage_port: SessionsStoragePort
) -> ResetPasswordHandler:
    return ResetPasswordHandler(users_port, tokens_port, sessions_storage_port)


def use_refresh_session_handler(
    users_port: UsersPort, sessions_storage_port: SessionsStoragePort, tokens_port: TokensPort
) -> RefreshSessionHandler:
    return RefreshSessionHandler(users_port, sessions_storage_port, tokens_port)


def use_login_handler(
    sessions_storage_port: SessionsStoragePort, tokens_port: TokensPort, users_port: UsersPort
) -> LoginHandler:
    return LoginHandler(sessions_storage_port, tokens_port, users_port)


def use_authenticate_handler(
    sessions_storage_port: SessionsStoragePort,
    tokens_port: TokensPort,
    users_port: UsersPort,
    files_port: FilesPort,
    user_events_port: UserEventsPort,
) -> AuthenticateHandler:
    return AuthenticateHandler(sessions_storage_port, tokens_port, users_port, files_port, user_events_port)


def use_generate_auth_session_handler(sessions_storage_port: SessionsStoragePort) -> GenerateAuthSessionHandler:
    return GenerateAuthSessionHandler(sessions_storage_port)


def use_send_verification_code_handler(
    sender: NotificationSenderPort, users_port: UsersPort, codes_storage_port: CodesStoragePort
) -> SendVerificationCodeHandler:
    return SendVerificationCodeHandler(sender, users_port, codes_storage_port)


def use_verify_code_handler(codes_storage_port: CodesStoragePort) -> VerifyCodeHandler:
    return VerifyCodeHandler(codes_storage_port)
