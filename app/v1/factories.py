from dataclasses import asdict, fields

from app.protobuf import users_pb2

from .graphql.graph_types import AuthData, UploadedFile, User
from .schemas import DbUser, SavedFile, UserAuthData


class UploadedFileFactory:

    @staticmethod
    def schema_from_pydantic(file: SavedFile) -> UploadedFile:
        include_fields = {field.name for field in fields(UploadedFile)}
        return UploadedFile(**file.model_dump(include=include_fields))


class UserFactory:

    @staticmethod
    def schema_from_db_user(user: DbUser) -> User:
        include_fields = {field.name for field in fields(User)}
        user_schema = User(**user.model_dump(include=include_fields))
        user_schema.avatar = UploadedFileFactory.schema_from_pydantic(user.avatar) if user.avatar else None
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
            original_avatar_url=user.avatar.original_url if user.avatar else None,
            converted_avatar_url=user.avatar.converted_url if user.avatar else None,
        )


class AuthDataFactory:

    @staticmethod
    def pydantic_from_schema(auth_data: AuthData) -> UserAuthData:
        auth_data_dict = asdict(auth_data)
        original_file = auth_data_dict["avatar_file"]["original_file"]
        original_file["system_filetype"] = original_file["system_filetype"].value
        converted_file = auth_data_dict["avatar_file"]["converted_file"]
        if converted_file:
            converted_file["system_filetype"] = converted_file["system_filetype"].value

        return UserAuthData.model_validate(auth_data_dict)
