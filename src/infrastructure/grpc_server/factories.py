from domain.files.models import SavedFile
from domain.users.models import User

from .usersprotobuf import users_pb2


class SavedFileProtoFactory:

    @staticmethod
    def proto_from_domain(file: SavedFile) -> users_pb2.SavedFile:
        return users_pb2.SavedFile(
            original_url=file.get_original_url(),
            original_filename=file.get_original_filename(),
            converted_url=file.get_converted_url(),
            converted_filename=file.get_converted_filename(),
        )


class UserProtoFactory:

    @staticmethod
    def proto_from_domain(user: User) -> users_pb2.UserResponse:
        if avatar := user.get_avatar():
            avatar_proto = SavedFileProtoFactory.proto_from_domain(avatar)
        else:
            avatar_proto = None

        return users_pb2.UserResponse(
            id=user.get_id(),
            username=user.get_username(),
            email=user.get_email(),
            phone=user.get_phone(),
            first_name=user.get_first_name(),
            last_name=user.get_last_name(),
            middle_name=user.get_middle_name(),
            status=user.get_status(),
            email_confirmed=user.get_email_confirmed(),
            phone_confirmed=user.get_phone_confirmed(),
            avatar=avatar_proto,
        )
