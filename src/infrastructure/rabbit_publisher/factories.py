from domain.users.models import User
from infrastructure.rabbit_publisher.dtos import (
    EventPermission,
    EventPermissionCategory,
    EventSavedFile,
    EventUser,
    SystemEvent,
)


class UserEventFactory:

    @staticmethod
    def event_from_model(user: User, event_type: str) -> SystemEvent:
        if avatar := user.get_avatar():
            event_user_avatar = EventSavedFile(
                originalUrl=avatar.get_original_url(),
                originalFilename=avatar.get_original_filename(),
                convertedUrl=avatar.get_converted_url(),
                convertedFilename=avatar.get_converted_filename(),
            )
        else:
            event_user_avatar = None

        event_permissions: list[EventPermission] = []
        for permission in user.get_permissions():
            if category := permission.get_category():
                event_category = EventPermissionCategory(
                    name=category.get_name(),
                    code=category.get_code(),
                )
            else:
                event_category = None

            event_permissions.append(
                EventPermission(
                    code=permission.get_code(),
                    name=permission.get_name(),
                    category=event_category,
                )
            )

        event_user = EventUser(
            id=user.get_id(),
            username=user.get_username(),
            first_name=user.get_first_name(),
            last_name=user.get_last_name(),
            email_confirmed=user.get_email_confirmed(),
            phone_confirmed=user.get_phone_confirmed(),
            last_seen=user.get_last_seen(),
            middle_name=user.get_middle_name(),
            avatar=event_user_avatar,
            phone=user.get_phone(),
            email=user.get_email(),
            status=user.get_status(),
            permissions=event_permissions,
        )
        system_event = SystemEvent(included_users=[], event_type=event_type, data=event_user.model_dump_json())
        return system_event
