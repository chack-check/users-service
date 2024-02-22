from dataclasses import asdict, fields

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
