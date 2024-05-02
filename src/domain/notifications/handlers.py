from domain.users.exceptions import UserNotFound
from domain.users.ports import UsersPort

from .ports import CodesStoragePort, NotificationSenderPort


class SendVerificationCodeHandler:

    def __init__(self, sender: NotificationSenderPort, users_port: UsersPort, codes_storage_port: CodesStoragePort):
        self._sender = sender
        self._users_port = users_port
        self._codes_storage_port = codes_storage_port

    async def execute(self, email_or_phone: str, check_user_existing: bool = False) -> None:
        if check_user_existing:
            user = await self._users_port.get_by_email_or_phone(email_or_phone)
            if not user:
                raise UserNotFound("user not found")

        code = await self._codes_storage_port.generate_verification_code(email_or_phone)
        await self._sender.send_code(email_or_phone, code)


class VerifyCodeHandler:

    def __init__(self, codes_storage_port: CodesStoragePort):
        self._codes_storage_port = codes_storage_port

    async def execute(self, email_or_phone: str, code: str) -> None:
        await self._codes_storage_port.validate_verification_code(email_or_phone, code)
