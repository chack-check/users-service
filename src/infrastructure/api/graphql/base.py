import logging
from typing import TypeAlias

import strawberry
from strawberry.types import Info

from domain.sessions.exceptions import (
    IncorrectAuthData,
    IncorrectTokenException,
    NoSessionsToRefreshException,
)
from domain.sessions.models import AuthSessionOperations as DomainAuthSessionOperation
from domain.users.exceptions import (
    IncorrectPasswordException,
    UserAlreadyExists,
    UserNotFound,
)
from infrastructure.api.factories import (
    AuthDataApiFactory,
    AuthenticationSessionApiFactory,
    LoginDataApiFactory,
    TokensApiFactory,
    UpdateDataApiFactory,
    UploadingFileApiFactory,
    UserApiFactory,
)
from infrastructure.database.base import session as db_session
from infrastructure.database.exceptions import IncorrectFileSignature
from infrastructure.dependencies import (
    use_authenticate_handler,
    use_codes_storage_adapter,
    use_files_adapter,
    use_generate_auth_session_handler,
    use_get_user_by_token_handler,
    use_get_user_handler,
    use_get_users_by_ids_handler,
    use_login_handler,
    use_refresh_handler,
    use_reset_password_handler,
    use_send_verification_code_handler,
    use_sessions_storage_adapter,
    use_tokens_adapter,
    use_update_avatar_handler,
    use_update_email_handler,
    use_update_me_handler,
    use_update_password_handler,
    use_update_phone_handler,
    use_user_events_adapter,
    use_users_adapter,
    use_verify_code_handler,
)
from infrastructure.memory_storage.exceptions import (
    IncorrectAuthenticationSession,
    IncorrectVerificationCode,
)
from infrastructure.senders.email import EmailSender, LoggingEmailSender

from ..dependencies import CustomContext
from .graph_types import (
    AuthData,
    AuthSessionOperations,
    AuthSessionResponse,
    ChangeEmailData,
    ChangePasswordData,
    ChangePhoneData,
    ErrorResponse,
    FieldError,
    FieldErrorsResponse,
    LoginData,
    Tokens,
    UpdateData,
    UploadFileData,
    User,
    UsersArrayResponse,
    VerificationSended,
    VerificationSources,
)

CustomInfo: TypeAlias = Info[CustomContext, None]

logger = logging.getLogger("uvicorn.error")


@strawberry.type
class Query:

    @strawberry.field
    async def user_me(self, info: CustomInfo) -> User | ErrorResponse:
        if not info.context.token:
            return ErrorResponse(message="Token required")

        try:
            async with db_session() as s:
                handler = use_get_user_by_token_handler(
                    use_users_adapter(s), use_tokens_adapter(), use_files_adapter(s)
                )
                user = await handler.execute(info.context.token)
                await s.commit()
                return UserApiFactory.response_from_domain(user)
        except IncorrectTokenException:
            return ErrorResponse(message="Incorrect token")
        except Exception:
            return ErrorResponse(message="Internal server error")

    @strawberry.field
    async def user(
        self, info: CustomInfo, id: int | None = None, username: str | None = None, email: str | None = None
    ) -> User | ErrorResponse:
        if not info.context.token:
            return ErrorResponse(message="Token required")

        try:
            async with db_session() as s:
                handler = use_get_user_by_token_handler(
                    use_users_adapter(s), use_tokens_adapter(), use_files_adapter(s)
                )
                await handler.execute(info.context.token)
                get_user_handler = use_get_user_handler(use_users_adapter(s), use_files_adapter(s))
                user = await get_user_handler.execute(id, username, email)
                await s.commit()
                return UserApiFactory.response_from_domain(user)
        except IncorrectTokenException:
            return ErrorResponse(message="Incorrect token")
        except UserNotFound:
            return ErrorResponse(message="User not found")
        except Exception:
            return ErrorResponse(message="Internal server error")

    @strawberry.field
    async def users_by_ids(self, info: CustomInfo, ids: list[int]) -> UsersArrayResponse | ErrorResponse:
        if not info.context.token:
            return ErrorResponse(message="Token required")

        try:
            async with db_session() as s:
                handler = use_get_user_by_token_handler(
                    use_users_adapter(s), use_tokens_adapter(), use_files_adapter(s)
                )
                await handler.execute(info.context.token)
                get_users_by_ids_handler = use_get_users_by_ids_handler(use_users_adapter(s), use_files_adapter(s))
                users = await get_users_by_ids_handler.execute(ids)
                await s.commit()
                return UsersArrayResponse(users=[UserApiFactory.response_from_domain(user) for user in users])
        except Exception:
            return ErrorResponse(message="Internal server error")


@strawberry.type
class Mutation:

    @strawberry.mutation
    async def login(self, info: CustomInfo, login_data: LoginData) -> Tokens | ErrorResponse:
        try:
            async with db_session() as s:
                login_handler = use_login_handler(
                    use_sessions_storage_adapter(), use_users_adapter(s), use_tokens_adapter()
                )
                domain_login_data = LoginDataApiFactory.domain_from_request(login_data)
                tokens = await login_handler.execute(domain_login_data)
                response = TokensApiFactory.response_from_domain(tokens)
                await s.commit()
                return response
        except UserNotFound:
            return ErrorResponse(message="Incorrect credentials")
        except Exception:
            return ErrorResponse(message="Internal server error")

    @strawberry.mutation
    async def send_verification_code(
        self,
        phone: str | None = None,
        email: str | None = None,
        check_user_existing: bool = False,
    ) -> VerificationSended | ErrorResponse:
        if not any((phone, email)):
            raise ValueError

        try:
            async with db_session() as s:
                sender = LoggingEmailSender(EmailSender())
                send_verification_code_handler = use_send_verification_code_handler(
                    sender, use_users_adapter(s), use_codes_storage_adapter()
                )
                await send_verification_code_handler.execute(
                    email if email else phone,  # pyright: ignore[reportArgumentType]
                    check_user_existing,
                )
                await s.commit()
                return VerificationSended(sended=True)
        except UserNotFound:
            return ErrorResponse(message="User not found")
        except Exception:
            return ErrorResponse(message="Internal server error")

    @strawberry.mutation
    async def verify_code(
        self, operation: AuthSessionOperations, code: str, field: str
    ) -> AuthSessionResponse | FieldErrorsResponse | ErrorResponse:
        try:
            verify_code_handler = use_verify_code_handler(use_codes_storage_adapter())
            await verify_code_handler.execute(field, code)
            generate_auth_session_handler = use_generate_auth_session_handler(use_sessions_storage_adapter())
            auth_session = await generate_auth_session_handler.execute(
                field, DomainAuthSessionOperation(operation.value)
            )
            return AuthenticationSessionApiFactory.response_from_domain(auth_session)
        except IncorrectVerificationCode:
            return FieldErrorsResponse(errors=[FieldError(field="code", errors=["Incorrect verification code"])])
        except Exception:
            return ErrorResponse(message="Internal server error")

    @strawberry.mutation
    async def authenticate(
        self, info: CustomInfo, session: str, verification_source: VerificationSources, auth_data: AuthData
    ) -> Tokens | ErrorResponse | FieldErrorsResponse:
        try:
            async with db_session() as s:
                authenticate_handler = use_authenticate_handler(
                    use_sessions_storage_adapter(),
                    use_users_adapter(s),
                    use_tokens_adapter(),
                    use_files_adapter(s),
                    use_user_events_adapter(),
                )
                auth_data_domain = AuthDataApiFactory.domain_from_request(auth_data)
                tokens = await authenticate_handler.execute(session, verification_source.value, auth_data_domain)
                response = TokensApiFactory.response_from_domain(tokens)
                await s.commit()
                return response
        except IncorrectAuthData as e:
            return ErrorResponse(message=e.args[0])
        except UserAlreadyExists:
            return ErrorResponse(message="User with these credentials already exists")
        except IncorrectFileSignature:
            return FieldErrorsResponse(errors=[FieldError(field="avatar", errors=["Incorrect file signature"])])
        except Exception:
            return ErrorResponse(message="Internal server error")

    @strawberry.mutation
    async def update_me(self, info: CustomInfo, update_data: UpdateData) -> User | ErrorResponse:
        if not info.context.token:
            return ErrorResponse(message="Token required")

        try:
            async with db_session() as s:
                handler = use_update_me_handler(
                    use_users_adapter(s),
                    use_tokens_adapter(),
                    use_user_events_adapter(),
                    use_files_adapter(s),
                )
                update_data_domain = UpdateDataApiFactory.domain_from_request(update_data)
                updated_user = await handler.execute(info.context.token, update_data_domain)
                await s.commit()
                return UserApiFactory.response_from_domain(updated_user)
        except IncorrectTokenException:
            return ErrorResponse(message="Incorrect token")
        except Exception:
            return ErrorResponse(message="Internal server error")

    @strawberry.mutation
    async def update_avatar(
        self, info: CustomInfo, new_avatar: UploadFileData | None
    ) -> User | ErrorResponse | FieldErrorsResponse:
        if not info.context.token:
            return ErrorResponse(message="Token required")

        try:
            async with db_session() as s:
                handler = use_update_avatar_handler(
                    use_users_adapter(s),
                    use_tokens_adapter(),
                    use_user_events_adapter(),
                    use_files_adapter(s),
                )
                new_avatar_domain = UploadingFileApiFactory.domain_from_request(new_avatar) if new_avatar else None
                updated_user = await handler.execute(info.context.token, new_avatar_domain)
                await s.commit()
                return UserApiFactory.response_from_domain(updated_user)
        except IncorrectTokenException:
            return ErrorResponse(message="Incorrect token")
        except IncorrectFileSignature:
            return FieldErrorsResponse(errors=[FieldError(field="avatar", errors=["Incorrect file signature"])])
        except Exception:
            return ErrorResponse(message="Internal server error")

    @strawberry.mutation
    async def refresh(self, info: CustomInfo) -> Tokens | ErrorResponse:
        if not info.context.token:
            return ErrorResponse(message="Token required")

        try:
            async with db_session() as s:
                handler = use_refresh_handler(
                    use_sessions_storage_adapter(),
                    use_users_adapter(s),
                    use_tokens_adapter(),
                )
                tokens = await handler.execute(info.context.token)
                tokens_response = TokensApiFactory.response_from_domain(tokens)
                await s.commit()
                return tokens_response
        except IncorrectTokenException:
            return ErrorResponse(message="Incorrect token")
        except NoSessionsToRefreshException:
            return ErrorResponse(message="You have no sessions. Try to relogin")
        except Exception:
            return ErrorResponse(message="Internal server error")

    @strawberry.mutation
    async def verify_field(self, info: CustomInfo, code: str, verification_source: VerificationSources) -> None: ...

    @strawberry.mutation
    async def update_password(self, info: CustomInfo, change_password_data: ChangePasswordData) -> User | ErrorResponse:
        if not info.context.token:
            return ErrorResponse(message="Token required")

        try:
            async with db_session() as s:
                handler = use_update_password_handler(
                    use_users_adapter(s),
                    use_tokens_adapter(),
                    use_files_adapter(s),
                )
                user = await handler.execute(
                    info.context.token, change_password_data.old_password, change_password_data.new_password
                )
                await s.commit()
                return UserApiFactory.response_from_domain(user)
        except IncorrectTokenException:
            return ErrorResponse(message="Incorrect token")
        except IncorrectPasswordException:
            return ErrorResponse(message="Incorrect password")
        except Exception:
            return ErrorResponse(message="Internal server error")

    @strawberry.mutation
    async def update_email(self, info: CustomInfo, change_email_data: ChangeEmailData) -> User | ErrorResponse:
        if not info.context.token:
            return ErrorResponse(message="Token required")

        try:
            async with db_session() as s:
                handler = use_update_email_handler(
                    use_sessions_storage_adapter(),
                    use_users_adapter(s),
                    use_tokens_adapter(),
                    use_user_events_adapter(),
                    use_files_adapter(s),
                )
                user = await handler.execute(
                    info.context.token,
                    change_email_data.session,
                    change_email_data.new_email,
                )
                await s.commit()
                return UserApiFactory.response_from_domain(user)
        except IncorrectTokenException:
            return ErrorResponse(message="Incorrect token")
        except Exception:
            return ErrorResponse(message="Internal server error")

    @strawberry.mutation
    async def update_phone(self, info: CustomInfo, change_phone_data: ChangePhoneData) -> User | ErrorResponse:
        if not info.context.token:
            return ErrorResponse(message="Token required")

        try:
            async with db_session() as s:
                handler = use_update_phone_handler(
                    use_sessions_storage_adapter(),
                    use_users_adapter(s),
                    use_tokens_adapter(),
                    use_user_events_adapter(),
                    use_files_adapter(s),
                )
                user = await handler.execute(
                    info.context.token,
                    change_phone_data.session,
                    change_phone_data.new_phone,
                )
                await s.commit()
                return UserApiFactory.response_from_domain(user)
        except IncorrectTokenException:
            return ErrorResponse(message="Incorrect token")
        except Exception:
            return ErrorResponse(message="Internal server error")

    @strawberry.mutation
    async def reset_password(
        self, info: CustomInfo, session: str, email_or_phone: str, new_password: str
    ) -> Tokens | ErrorResponse:
        try:
            async with db_session() as s:
                handler = use_reset_password_handler(
                    use_sessions_storage_adapter(),
                    use_users_adapter(s),
                    use_tokens_adapter(),
                )
                tokens = await handler.execute(session, email_or_phone, new_password)
                tokens_response = TokensApiFactory.response_from_domain(tokens)
                await s.commit()
                return tokens_response
        except UserNotFound:
            return ErrorResponse(message="User with this email or phone not found")
        except IncorrectAuthenticationSession:
            return ErrorResponse(message="Invalid authentication session")
        except Exception:
            return ErrorResponse(message="Internal server error")
