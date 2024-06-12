from abc import ABC, abstractmethod

from domain.general.models import PaginatedResponse

from .models import User


class UsersPort(ABC):

    @abstractmethod
    async def get_by_phone_or_username(self, phone_or_username: str) -> User | None: ...

    @abstractmethod
    async def get_by_email_or_phone(self, email_or_phone: str) -> User | None: ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def get_by_ids(self, ids: list[int]) -> list[User]: ...

    @abstractmethod
    async def get_by_phone(self, phone: str) -> User | None: ...

    @abstractmethod
    async def search_users(self, query: str, page: int = 1, per_page: int = 100) -> PaginatedResponse[User]: ...

    @abstractmethod
    async def save(self, user: User) -> User: ...


class UserEventsPort:

    @abstractmethod
    async def send_user_created(self, user: User) -> None: ...

    @abstractmethod
    async def send_user_changed(self, user: User) -> None: ...
