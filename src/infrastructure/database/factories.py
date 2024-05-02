from typing import Any

from domain.files.models import SavedFile
from domain.permissions.models import Permission, PermissionCategory
from domain.users.models import User

from .models import Permission as PermissionModel
from .models import PermissionCategory as PermissionCategoryModel
from .models import User as UserModel
from .models import UserAvatar


class SavedFileFactory:

    @staticmethod
    def domain_from_orm(avatar: UserAvatar) -> SavedFile:
        return SavedFile(
            id_=avatar.id,
            original_url=avatar.original_url,
            original_filename=avatar.original_filename,
            converted_url=avatar.converted_url if avatar.converted_url else None,
            converted_filename=avatar.converted_filename if avatar.converted_filename else None,
        )

    @staticmethod
    def dict_from_domain(file: SavedFile) -> dict[str, Any]:
        return {
            "original_url": file.get_original_url(),
            "original_filename": file.get_original_filename(),
            "converted_url": file.get_converted_url(),
            "converted_filename": file.get_converted_filename(),
        }


class PermissionCategoryFactory:

    @staticmethod
    def domain_from_orm(category: PermissionCategoryModel) -> PermissionCategory:
        return PermissionCategory(
            code=category.code,
            name=category.name,
        )


class PermissionFactory:

    @staticmethod
    def domain_from_orm(permission: PermissionModel) -> Permission:
        return Permission(
            name=permission.name,
            code=permission.code,
            category=PermissionCategoryFactory.domain_from_orm(permission.category) if permission.category else None,
        )


class UserFactory:

    @staticmethod
    def domain_from_orm(user: UserModel) -> User:
        return User(
            id_=user.id,
            username=user.username,
            password=user.password,
            first_name=user.first_name,
            last_name=user.last_name,
            email_confirmed=user.email_confirmed,
            phone_confirmed=user.phone_confirmed,
            last_seen=user.last_seen,
            middle_name=user.middle_name,
            avatar=SavedFileFactory.domain_from_orm(user.avatar) if user.avatar else None,
            phone=user.phone,
            email=user.email,
            status=user.status,
            permissions=[PermissionFactory.domain_from_orm(p) for p in user.permissions],
        )

    @staticmethod
    def dict_from_domain(user: User, avatar_id: int | None = None) -> dict[str, Any]:
        return {
            "username": user.get_username(),
            "avatar_id": avatar_id,
            "phone": user.get_phone(),
            "email": user.get_email(),
            "password": user.get_password(),
            "first_name": user.get_first_name(),
            "last_name": user.get_last_name(),
            "middle_name": user.get_middle_name(),
            "status": user.get_status(),
            "email_confirmed": user.get_email_confirmed(),
            "phone_confirmed": user.get_phone_confirmed(),
            "last_seen": user.get_last_seen(),
        }
