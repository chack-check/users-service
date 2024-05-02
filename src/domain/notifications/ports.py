from abc import ABC, abstractmethod


class CodesStoragePort(ABC):

    @abstractmethod
    async def generate_verification_code(self, email_or_phone: str) -> str: ...

    @abstractmethod
    async def validate_verification_code(self, email_or_phone: str, code: str) -> None: ...


class NotificationSenderPort(ABC):

    @abstractmethod
    async def send_code(self, identifier: str, code: str) -> None: ...
