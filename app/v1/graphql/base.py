from typing import TypeAlias
import strawberry
from strawberry.types import Info

from ..services.users import UsersSet
from ..services.verifications import verify_signature
from ..senders.email import EmailSender
from ..senders.phone import PhoneSender
from ..dependencies import CustomContext
from ..utils import (
    validate_user_required,
    get_schema_from_pydantic,
    get_pydantic_from_schema,
)
from ..exceptions import IncorrectVerificationSource
from ..schemas import (
    UserUpdateData,
    UserAuthData,
    UserLoginData,
)
from .graph_types import (
    User, PaginatedUsersResponse, LoginData, Tokens,
    AuthData, UpdateData, ChangePasswordData,
    ChangeEmailData, VerificationSended,
    VerificationSources,
)


CustomInfo: TypeAlias = Info[CustomContext, None]


@strawberry.type
class Query:

    @strawberry.field
    async def user_me(self, info: CustomInfo) -> User:
        validate_user_required(info.context.user)
        return get_schema_from_pydantic(User, info.context.user)

    @strawberry.field
    async def user(self, info: CustomInfo,
                   id: int | None = None,
                   username: str | None = None,
                   email: str | None = None) -> User:
        validate_user_required(info.context.user)
        user = await info.context.users_set.get(
            id=id, username=username, email=email
        )
        return get_schema_from_pydantic(User, user)

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
        users_list = [get_schema_from_pydantic(
            User, u
        ) for u in paginated_users.data]
        return PaginatedUsersResponse(
            page=paginated_users.page,
            num_pages=paginated_users.num_pages,
            per_page=paginated_users.per_page,
            data=users_list
        )


@strawberry.type
class Mutation:

    @strawberry.mutation
    async def login(info: CustomInfo, login_data: LoginData) -> Tokens:
        users_set: UsersSet = info.context.users_set
        data = get_pydantic_from_schema(login_data, UserLoginData)
        tokens = await users_set.login(data)
        return get_schema_from_pydantic(Tokens, tokens)

    @strawberry.mutation
    async def send_verification_code(
        info: CustomInfo,
        signature: str,
        phone: str | None = None,
        email: str | None = None,
    ) -> VerificationSended:
        verify_signature(phone or email, signature)
        if not any((phone, email)) or all((phone, email)):
            raise IncorrectVerificationSource

        verificator = info.context.verificator
        sender = EmailSender() if email else PhoneSender()
        code = await verificator.create_verification_code(
            email if email else phone
        )
        info.context.background_tasks.add_task(
            sender.send_verification_code,
            email if email else phone, code
        )
        return VerificationSended(sended=True)

    @strawberry.mutation
    async def authenticate(info: CustomInfo,
                           code: str,
                           verification_source: VerificationSources,
                           auth_data: AuthData) -> Tokens:
        users_set = info.context.users_set
        data = get_pydantic_from_schema(auth_data, UserAuthData)
        verificator = info.context.verificator
        field: str = getattr(auth_data, verification_source.value)
        await verificator.verify_code(field, code)
        tokens = await users_set.authenticate(data)
        await users_set.confirm_field(tokens.user, verification_source.value)
        return get_schema_from_pydantic(Tokens, tokens)

    @strawberry.mutation
    async def update_me(info: CustomInfo,
                        update_data: UpdateData) -> User:
        validate_user_required(info.context.user)
        users_set = info.context.users_set
        data = get_pydantic_from_schema(update_data, UserUpdateData)
        updated_user = await users_set.update(info.context.user, data)
        return get_schema_from_pydantic(User, updated_user)

    @strawberry.mutation
    async def refresh(info: CustomInfo) -> Tokens:
        validate_user_required(info.context.user)
        users_set = info.context.users_set
        tokens = await users_set.refresh(info.context.user, info.context.token)
        return get_schema_from_pydantic(Tokens, tokens)

    @strawberry.mutation
    async def verify_field(
            info: CustomInfo, code: str,
            verification_source: VerificationSources
    ) -> None:
        validate_user_required()
        verificator = info.context.verificator
        users_set = info.context.users_set
        user = info.context.user
        user_field = getattr(user, verification_source.value)
        await verificator.verify_code(user_field, code)
        await users_set.confirm_field(user, verification_source.value)

    @strawberry.mutation
    async def update_password(
        change_password_data: ChangePasswordData
    ) -> User:
        ...

    @strawberry.mutation
    async def update_email(
        change_email_data: ChangeEmailData
    ) -> User:
        ...
