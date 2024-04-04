from dataclasses import asdict, fields
from urllib.parse import urljoin

from app.project.settings import settings
from app.protobuf import users_pb2

from .graphql.graph_types import (
    AuthData,
    Permission,
    PermissionCategory,
    UploadedFile,
    UploadFileData,
    User,
)
from .schemas import (
    DbUser,
    PermissionCategoryDto,
    PermissionDto,
    SavedFile,
    SavingFileData,
    SavingFileObject,
    SavingFileSystemFiletypes,
    UserAuthData,
    UserEvent,
)


def get_default_avatar_url(username: str) -> str:
    return urljoin(settings.avatar_service_url, f"?squares=8&size=128&word={username}")


class UploadedFileFactory:

    @staticmethod
    def schema_from_pydantic(file: SavedFile) -> UploadedFile:
        include_fields = {field.name for field in fields(UploadedFile)}
        return UploadedFile(**file.model_dump(include=include_fields))

    @staticmethod
    def default_schema_from_username(username: str) -> UploadedFile:
        file_url = get_default_avatar_url(username)
        filename = f"{username}.svg"
        return UploadedFile(original_url=file_url, original_filename=filename)


class PermissionCategoryFactory:

    @staticmethod
    def schema_from_dto(category: PermissionCategoryDto) -> PermissionCategory:
        return PermissionCategory(**category.model_dump())


class PermissionFactory:

    @staticmethod
    def schema_from_dto(permission: PermissionDto) -> Permission:
        permission_schema = Permission(**permission.model_dump(exclude={"category", "id"}))
        permission_schema.category = (
            PermissionCategoryFactory.schema_from_dto(permission.category) if permission.category else None
        )
        return permission_schema


class UserFactory:

    @staticmethod
    def schema_from_db_user(user: DbUser) -> User:
        include_fields = {field.name for field in fields(User)}
        user_schema = User(**user.model_dump(include=include_fields, exclude={"permissions"}))
        if user.avatar:
            user_schema.avatar = UploadedFileFactory.schema_from_pydantic(user.avatar)
        else:
            user_schema.avatar = UploadedFileFactory.default_schema_from_username(user.username)

        user_schema.permissions = [PermissionFactory.schema_from_dto(permission) for permission in user.permissions]
        return user_schema

    @staticmethod
    def get_grpc_from_db_user(user: DbUser) -> users_pb2.UserResponse:
        return users_pb2.UserResponse(
            id=user.id,
            username=user.username,
            phone=user.phone,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            activity=user.activity,
            status=user.status,
            email_confirmed=user.email_confirmed,
            phone_confirmed=user.phone_confirmed,
            last_seen=user.last_seen.isoformat(),
            original_avatar_url=(
                user.avatar.original_url
                if user.avatar and user.avatar.original_url
                else get_default_avatar_url(user.username)
            ),
            converted_avatar_url=user.avatar.converted_url if user.avatar and user.avatar.converted_url else None,
        )

    @staticmethod
    def event_from_dto(user: DbUser, event_type: str, included_users: list[int] | None = None) -> UserEvent:
        user_copy = user.model_copy(deep=True)
        if not user_copy.avatar:
            user_copy.avatar = SavedFile(
                original_url=get_default_avatar_url(user_copy.username), original_filename=f"{user_copy.username}.svg"
            )

        return UserEvent(
            event_type=event_type,
            included_users=included_users if included_users else [],
            data=user_copy.model_dump_json(exclude={"password"}),
        )


class FileFactory:

    @staticmethod
    def pydantic_from_schema(file: UploadFileData) -> SavingFileData:
        return SavingFileData(
            original_file=SavingFileObject(
                filename=file.original_file.filename,
                url=file.original_file.url,
                signature=file.original_file.signature,
                system_filetype=SavingFileSystemFiletypes(file.original_file.system_filetype.value),
            ),
            converted_file=(
                SavingFileObject(
                    filename=file.converted_file.filename,
                    url=file.converted_file.url,
                    signature=file.converted_file.signature,
                    system_filetype=SavingFileSystemFiletypes(file.converted_file.system_filetype.value),
                )
                if file.converted_file
                else None
            ),
        )


class AuthDataFactory:

    @staticmethod
    def pydantic_from_schema(auth_data: AuthData) -> UserAuthData:
        auth_data_dict = asdict(auth_data)
        if not auth_data_dict.get("avatar_file"):
            return UserAuthData.model_validate(auth_data_dict)

        if original_file := auth_data_dict["avatar_file"].get("original_file"):
            original_file["system_filetype"] = original_file["system_filetype"].value
        if converted_file := auth_data_dict["avatar_file"].get("system_filetype"):
            converted_file["system_filetype"] = converted_file["system_filetype"].value

        return UserAuthData.model_validate(auth_data_dict)
