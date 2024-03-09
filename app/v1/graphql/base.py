from typing import TypeAlias

import strawberry
from strawberry.types import Info

from app.v1.factories import AuthDataFactory, FileFactory, UserFactory

from ..dependencies import CustomContext
from ..exceptions import IncorrectVerificationSource
from ..schemas import UserLoginData, UserUpdateData
from ..senders.email import EmailSender
from ..senders.phone import PhoneSender
from ..services.users import UsersSet
from ..utils import (
    get_pydantic_from_schema,
    get_schema_from_pydantic,
    validate_auth_data,
    validate_user_required,
)
from .graph_types import (
    AuthData,
    AuthSessionResponse,
    ChangeEmailData,
    ChangePasswordData,
    ChangePhoneData,
    LoginData,
    PaginatedUsersResponse,
    Tokens,
    UpdateData,
    UploadFileData,
    User,
    VerificationSended,
    VerificationSources,
)

CustomInfo: TypeAlias = Info[CustomContext, None]


@strawberry.type
class Query:

    @strawberry.field
    async def user_me(self, info: CustomInfo) -> User:
        validate_user_required(info.context.user)
        assert info.context.user
        user_schema = UserFactory.schema_from_db_user(info.context.user)
        return user_schema

    @strawberry.field
    async def user(self, info: CustomInfo,
                   id: int | None = None,
                   username: str | None = None,
                   email: str | None = None) -> User:
        validate_user_required(info.context.user)
        user = await info.context.users_set.get(
            id=id, username=username, email=email
        )
        return UserFactory.schema_from_db_user(user)

    @strawberry.field
    async def users(self,
                    info: CustomInfo,
                    query: str = '',
                    page: int = 1,
                    per_page: int = 20) -> PaginatedUsersResponse:
        validate_user_required(info.context.user)
        paginated_users = await info.context.users_set.search(
            query=query, page=page, per_page=per_page
        )
        users_list = [UserFactory.schema_from_db_user(u) for u in paginated_users.data]
        return PaginatedUsersResponse(
            page=paginated_users.page,
            num_pages=paginated_users.num_pages,
            per_page=paginated_users.per_page,
            data=users_list
        )

    @strawberry.field
    async def users_by_ids(self, info: CustomInfo,
                           ids: list[int]) -> list[User]:
        validate_user_required(info.context.user)
        users = await info.context.users_set.get_by_ids(ids)
        users_list = [UserFactory.schema_from_db_user(u) for u in users]
        return users_list


@strawberry.type
class Mutation:

    @strawberry.mutation
    async def login(self, info: CustomInfo, login_data: LoginData) -> Tokens:
        users_set: UsersSet = info.context.users_set
        data = get_pydantic_from_schema(login_data, UserLoginData)
        tokens = await users_set.login(data)
        return get_schema_from_pydantic(Tokens, tokens)

    @strawberry.mutation
    async def send_verification_code(
        self,
        info: CustomInfo,
        phone: str | None = None,
        email: str | None = None,
        check_user_existing: bool = False,
    ) -> VerificationSended:
        field_value = phone if phone else email
        assert field_value
        if not any((phone, email)) or all((phone, email)):
            raise IncorrectVerificationSource

        if check_user_existing:
            users_set = info.context.users_set
            await users_set.get(
                email=email if email else None,
                phone=phone if phone else None
            )

        verificator = info.context.verificator
        sender = EmailSender() if email else PhoneSender()
        code = await verificator.create_verification_code(field_value)
        assert info.context.background_tasks
        info.context.background_tasks.add_task(
            sender.send_verification_code, [field_value], code
        )
        return VerificationSended(sended=True)

    @strawberry.mutation
    async def verify_code(self,
                          info: CustomInfo,
                          code: str,
                          field: str) -> AuthSessionResponse:
        verificator = info.context.verificator
        await verificator.verify_code(field, code)
        session = await verificator.get_authentication_session(field)
        return get_schema_from_pydantic(AuthSessionResponse, session)

    @strawberry.mutation
    async def authenticate(self,
                           info: CustomInfo,
                           session: str,
                           verification_source: VerificationSources,
                           auth_data: AuthData) -> Tokens:
        validate_auth_data(auth_data)
        users_set = info.context.users_set
        data = AuthDataFactory.pydantic_from_schema(auth_data)
        verificator = info.context.verificator
        if data.avatar_file:
            verificator.verify_file(data.avatar_file)

        field: str = getattr(auth_data, verification_source.value)
        await verificator.verify_auth_session(field, session)
        tokens = await users_set.authenticate(data)
        await users_set.confirm_field(tokens.user, verification_source.value)
        await verificator.clear_verifications(field)
        return get_schema_from_pydantic(Tokens, tokens)

    @strawberry.mutation
    async def update_me(self, info: CustomInfo,
                        update_data: UpdateData) -> User:
        validate_user_required(info.context.user)
        assert info.context.user
        users_set = info.context.users_set
        data = get_pydantic_from_schema(update_data, UserUpdateData)
        updated_user = await users_set.update(info.context.user, data)
        return UserFactory.schema_from_db_user(updated_user)

    @strawberry.mutation
    async def update_avatar(self, info: CustomInfo, new_avatar: UploadFileData | None) -> User:
        validate_user_required(info.context.user)
        assert info.context.user
        users_set = info.context.users_set
        new_avatar_data = FileFactory.pydantic_from_schema(new_avatar) if new_avatar else None
        if new_avatar_data:
            info.context.verificator.verify_file(new_avatar_data)

        db_user = await users_set.update_avatar(info.context.user, new_avatar_data)
        return UserFactory.schema_from_db_user(db_user)

    @strawberry.mutation
    async def refresh(self, info: CustomInfo) -> Tokens:
        validate_user_required(info.context.user)
        assert info.context.user
        assert info.context.token
        users_set = info.context.users_set
        tokens = await users_set.refresh(info.context.user, info.context.token)
        return get_schema_from_pydantic(Tokens, tokens)

    @strawberry.mutation
    async def verify_field(
            self, info: CustomInfo, code: str,
            verification_source: VerificationSources
    ) -> None:
        validate_user_required(info.context.user)
        verificator = info.context.verificator
        users_set = info.context.users_set
        user = info.context.user
        assert user
        user_field = getattr(user, verification_source.value)
        await verificator.verify_code(user_field, code)
        await users_set.confirm_field(user, verification_source.value)

    @strawberry.mutation
    async def update_password(
        self, info: CustomInfo, change_password_data: ChangePasswordData
    ) -> User:
        validate_user_required(info.context.user)
        assert info.context.user
        users_set = info.context.users_set
        new_db_user = await users_set.update_password(
            info.context.user, change_password_data.old_password, change_password_data.new_password
        )
        return UserFactory.schema_from_db_user(new_db_user)

    @strawberry.mutation
    async def update_email(
        self, info: CustomInfo, change_email_data: ChangeEmailData
    ) -> User:
        validate_user_required(info.context.user)
        assert info.context.user
        users_set = info.context.users_set
        await info.context.verificator.verify_auth_session(change_email_data.new_email, change_email_data.session)
        new_db_user = await users_set.update_email(
            info.context.user, change_email_data.new_email
        )
        return UserFactory.schema_from_db_user(new_db_user)

    @strawberry.mutation
    async def update_phone(
        self, info: CustomInfo, change_phone_data: ChangePhoneData
    ) -> User:
        validate_user_required(info.context.user)
        assert info.context.user
        users_set = info.context.users_set
        await info.context.verificator.verify_auth_session(change_phone_data.old_phone, change_phone_data.session)
        new_db_user = await users_set.update_phone(
            info.context.user, change_phone_data.new_phone
        )
        return UserFactory.schema_from_db_user(new_db_user)

    @strawberry.mutation
    async def reset_password(self,
                             info: CustomInfo,
                             session: str,
                             email_or_phone: str,
                             new_password: str) -> Tokens:
        users_set = info.context.users_set
        verificator = info.context.verificator
        await verificator.verify_auth_session(email_or_phone, session)
        db_user = await users_set.reset_password(email_or_phone, new_password)
        tokens = users_set.generate_tokens(db_user)
        return get_schema_from_pydantic(Tokens, tokens)
