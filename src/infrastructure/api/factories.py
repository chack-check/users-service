from domain.files.models import SavedFile, SystemFiletypes
from domain.files.models import UploadingFile as UploadingFileDomain
from domain.files.models import UploadingFileMeta
from domain.permissions.models import Permission as PermissionDomain
from domain.permissions.models import PermissionCategory as PermissionCategoryDomain
from domain.sessions.exceptions import IncorrectAuthData
from domain.sessions.models import AuthData as AuthDataDomain
from domain.sessions.models import AuthenticationSession
from domain.sessions.models import LoginData as LoginDataDomain
from domain.sessions.models import TokenPairData
from domain.users.models import UpdateData as UpdateDataDomain
from domain.users.models import User as UserDomain
from infrastructure.api.graphql.graph_types import (
    AuthData,
    AuthSessionResponse,
    LoginData,
    Permission,
    PermissionCategory,
    Tokens,
    UpdateData,
    UploadedFile,
    UploadFileData,
    UploadFileObject,
    User,
)


class UploadingFileMetaApiFactory:

    @staticmethod
    def domain_from_request(file: UploadFileObject) -> UploadingFileMeta:
        return UploadingFileMeta(
            url=file.url,
            signature=file.signature,
            filename=file.filename,
            system_filetype=SystemFiletypes(file.system_filetype.value),
        )


class UploadingFileApiFactory:

    @staticmethod
    def domain_from_request(file: UploadFileData) -> UploadingFileDomain:
        return UploadingFileDomain(
            original=UploadingFileMetaApiFactory.domain_from_request(file.original_file),
            converted=(
                UploadingFileMetaApiFactory.domain_from_request(file.converted_file) if file.converted_file else None
            ),
        )


class SavedFileApiFactory:

    @staticmethod
    def response_from_domain(file: SavedFile) -> UploadedFile:
        return UploadedFile(
            original_url=file.get_original_url(),
            original_filename=file.get_original_filename(),
            converted_url=file.get_converted_url(),
            converted_filename=file.get_converted_filename(),
        )


class PermissionCategoryApiFactory:

    @staticmethod
    def response_from_domain(category: PermissionCategoryDomain) -> PermissionCategory:
        return PermissionCategory(
            code=category.get_code(),
            name=category.get_name(),
        )


class PermissionApiFactory:

    @staticmethod
    def response_from_domain(permission: PermissionDomain) -> Permission:
        if category := permission.get_category():
            category_response = PermissionCategoryApiFactory.response_from_domain(category)
        else:
            category_response = None

        return Permission(
            code=permission.get_code(),
            name=permission.get_name(),
            category=category_response,
        )


class UserApiFactory:

    @staticmethod
    def response_from_domain(user: UserDomain) -> User:
        if avatar := user.get_avatar():
            avatar_response = SavedFileApiFactory.response_from_domain(avatar)
        else:
            avatar_response = None

        return User(
            id=user.get_id(),
            username=user.get_username(),
            phone=user.get_phone(),
            email=user.get_email(),
            first_name=user.get_first_name(),
            last_name=user.get_last_name(),
            middle_name=user.get_middle_name(),
            status=user.get_status(),
            email_confirmed=user.get_email_confirmed(),
            phone_confirmed=user.get_phone_confirmed(),
            last_seen=user.get_last_seen(),
            avatar=avatar_response,
            permissions=[PermissionApiFactory.response_from_domain(p) for p in user.get_permissions()],
        )


class TokensApiFactory:

    @staticmethod
    def response_from_domain(tokens: TokenPairData) -> Tokens:
        return Tokens(
            access_token=tokens.get_access_token(),
            refresh_token=tokens.get_refresh_token(),
        )


class AuthenticationSessionApiFactory:

    @staticmethod
    def response_from_domain(session: AuthenticationSession) -> AuthSessionResponse:
        return AuthSessionResponse(
            session=session.get_session(),
            exp=session.get_exp(),
        )


class AuthDataApiFactory:

    @staticmethod
    def domain_from_request(data: AuthData) -> AuthDataDomain:
        if data.password != data.password_repeat:
            raise IncorrectAuthData("passwords not match")

        return AuthDataDomain(
            username=data.username,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
            middle_name=data.middle_name,
            email=data.email,
            phone=data.phone,
            avatar=UploadingFileApiFactory.domain_from_request(data.avatar_file) if data.avatar_file else None,
        )


class LoginDataApiFactory:

    @staticmethod
    def domain_from_request(data: LoginData) -> LoginDataDomain:
        return LoginDataDomain(
            phone_or_username=data.phone_or_username,
            password=data.password,
        )


class UpdateDataApiFactory:

    @staticmethod
    def domain_from_request(data: UpdateData) -> UpdateDataDomain:
        return UpdateDataDomain(
            first_name=data.first_name,
            last_name=data.last_name,
            middle_name=data.middle_name,
            status=data.status,
        )
