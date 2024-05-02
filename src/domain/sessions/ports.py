from abc import ABC, abstractmethod
from typing import Literal

from domain.sessions.models import AuthenticationSession, AuthSessionOperations, Session
from domain.users.models import User


class SessionsStoragePort(ABC):

    @abstractmethod
    async def has_session(self, session: Session) -> bool: ...

    @abstractmethod
    async def save(self, session: Session) -> Session: ...

    @abstractmethod
    async def delete(self, session: Session) -> None: ...

    @abstractmethod
    async def delete_all(self, user: User) -> None: ...

    @abstractmethod
    async def verify_auth_session(
        self, email_or_phone: str, operation: AuthSessionOperations, session: str
    ) -> None: ...

    @abstractmethod
    async def generate_auth_session(
        self,
        email_or_phone: str,
        operation: AuthSessionOperations,
    ) -> AuthenticationSession: ...


class TokensPort(ABC):

    @abstractmethod
    def create_token(self, user: User, type: Literal["access", "refresh"]) -> str: ...

    @abstractmethod
    async def decode_token(self, token: str) -> int: ...
