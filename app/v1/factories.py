from dataclasses import asdict, fields
from urllib.parse import urljoin

from app.project.settings import settings
from app.protobuf import users_pb2

from .graphql.graph_types import AuthData, UploadedFile, User
from .schemas import DbUser, SavedFile, UserAuthData


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


class UserFactory:

    @staticmethod
    def schema_from_db_user(user: DbUser) -> User:
        include_fields = {field.name for field in fields(User)}
        user_schema = User(**user.model_dump(include=include_fields))
        if user.avatar:
            user_schema.avatar = UploadedFileFactory.schema_from_pydantic(user.avatar)
        else:
            user_schema.avatar = UploadedFileFactory.default_schema_from_username(user.username)

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
            original_avatar_url=user.avatar.original_url if user.avatar and user.avatar.original_url else get_default_avatar_url(user.username),
            converted_avatar_url=user.avatar.converted_url if user.avatar and user.avatar.converted_url else None,
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
