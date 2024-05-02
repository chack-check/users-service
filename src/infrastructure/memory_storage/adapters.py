import random
import string
from datetime import datetime, timedelta
from logging import getLogger
from zoneinfo import ZoneInfo

from redis.asyncio.client import Redis

from domain.notifications.ports import CodesStoragePort
from domain.sessions.models import AuthenticationSession, AuthSessionOperations, Session
from domain.sessions.ports import SessionsStoragePort
from domain.users.models import User
from infrastructure.memory_storage.exceptions import (
    IncorrectAuthenticationSession,
    IncorrectVerificationCode,
    VerificationAttemptsExpired,
)
from infrastructure.settings import settings

logger = getLogger("uvicorn.error")


class CodesStorageLoggingAdapter(CodesStoragePort):

    def __init__(self, adapter: CodesStoragePort):
        self._adapter = adapter

    async def generate_verification_code(self, email_or_phone: str) -> str:
        logger.debug(f"generating verification code for: {email_or_phone=}")
        try:
            code = await self._adapter.generate_verification_code(email_or_phone)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"fetched code: {code=}")
        return code

    async def validate_verification_code(self, email_or_phone: str, code: str) -> None:
        logger.debug(f"validating verification code: {email_or_phone=} {code=}")
        try:
            await self._adapter.validate_verification_code(email_or_phone, code)
        except Exception as e:
            logger.exception(e)
            raise


class CodesStorageAdapter(CodesStoragePort):

    def __init__(self, db: Redis):
        self._db = db

    def _get_verification_key(self, email_or_phone: str) -> str:
        return f"verification:{email_or_phone}"

    def _get_verification_attempts_key(self, email_or_phone: str) -> str:
        return f"verification:{email_or_phone}:attempts"

    def _generate_code(self, n: int = 6) -> str:
        return "".join([str(random.randint(0, 9)) for _ in range(n)])

    async def _increment_attempts(self, email_or_phone: str) -> None:
        key = self._get_verification_attempts_key(email_or_phone)
        await self._db.incr(key)

    async def _validate_attempts(self, email_or_phone: str) -> None:
        await self._increment_attempts(email_or_phone)
        attempts_key = self._get_verification_attempts_key(email_or_phone)
        attempts = await self._db.get(attempts_key)
        if attempts and int(attempts) > settings.verification_attempts_count:
            raise VerificationAttemptsExpired

    async def generate_verification_code(self, email_or_phone: str) -> str:
        verification_key = self._get_verification_key(email_or_phone)
        code = self._generate_code()
        await self._db.setex(verification_key, settings.verification_exp_seconds, code)
        attempts_key = self._get_verification_attempts_key(email_or_phone)
        await self._db.setex(attempts_key, settings.verification_exp_seconds, 0)
        return code

    async def validate_verification_code(self, email_or_phone: str, code: str) -> None:
        await self._validate_attempts(email_or_phone)
        key = self._get_verification_key(email_or_phone)
        right_code = await self._db.get(key)
        if not right_code or right_code.decode() != code:
            raise IncorrectVerificationCode


class SessionsStorageLoggingAdapter(SessionsStoragePort):

    def __init__(self, adapter: SessionsStoragePort):
        self._adapter = adapter

    async def has_session(self, session: Session) -> bool:
        logger.debug(f"validating has session: {session=}")
        try:
            has = await self._adapter.has_session(session)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"has session: {has}")
        return has

    async def save(self, session: Session) -> Session:
        logger.debug(f"saving session: {session=}")
        try:
            saved_session = await self._adapter.save(session)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"saved session: {saved_session}")
        return saved_session

    async def delete(self, session: Session) -> None:
        logger.debug(f"deleting session: {session=}")
        try:
            await self._adapter.delete(session)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"session deleted")

    async def delete_all(self, user: User) -> None:
        logger.debug(f"deleting all sessions for: {user=}")
        try:
            await self._adapter.delete_all(user)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"deleted all sessions")

    async def verify_auth_session(self, email_or_phone: str, operation: AuthSessionOperations, session: str) -> None:
        logger.debug(f"verifying auth session: {email_or_phone=} {operation=} {session=}")
        try:
            await self._adapter.verify_auth_session(email_or_phone, operation, session)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"veryfied auth session")

    async def generate_auth_session(
        self, email_or_phone: str, operation: AuthSessionOperations
    ) -> AuthenticationSession:
        logger.debug(f"generating auth session for: {email_or_phone=} {operation=}")
        try:
            session = await self._adapter.generate_auth_session(email_or_phone, operation)
        except Exception as e:
            logger.exception(e)
            raise

        logger.debug(f"generated auth session: {session=}")
        return session


class SessionsStorageAdapter(SessionsStoragePort):

    def __init__(self, redis_db: Redis):
        self._db = redis_db

    def _get_user_sessions_key(self, user_id: int) -> str:
        return f"sessions:{user_id}"

    async def has_session(self, session: Session) -> bool:
        sessions_key = self._get_user_sessions_key(session.get_user().get_id())
        return await self._db.sismember(sessions_key, session.get_refresh_token())

    async def save(self, session: Session) -> Session:
        sessions_key = self._get_user_sessions_key(session.get_user().get_id())
        await self._db.sadd(sessions_key, session.get_refresh_token())
        return session

    async def delete(self, session: Session) -> None:
        sessions_key = self._get_user_sessions_key(session.get_user().get_id())
        await self._db.srem(sessions_key, session.get_refresh_token())

    async def delete_all(self, user: User) -> None:
        sessions_key = self._get_user_sessions_key(user.get_id())
        await self._db.delete(sessions_key)

    async def verify_auth_session(self, email_or_phone: str, operation: AuthSessionOperations, session: str) -> None:
        session_key = self._get_auth_session_key(email_or_phone, operation.value)
        right_session = await self._db.get(session_key)
        if not right_session or right_session.decode() != session:
            raise IncorrectAuthenticationSession("incorrect authentication session")

    def _generate_session(self) -> str:
        return "".join(random.choice(string.hexdigits) for _ in range(32))

    def _get_auth_session_key(self, email_or_phone: str, operation: str) -> str:
        return f"authsession:{email_or_phone}:{operation}"

    async def generate_auth_session(
        self, email_or_phone: str, operation: AuthSessionOperations
    ) -> AuthenticationSession:
        session_key = self._get_auth_session_key(email_or_phone, operation.value)
        session_value = self._generate_session()
        await self._db.setex(session_key, settings.auth_session_exp_seconds, session_value)
        exp = datetime.now(ZoneInfo("UTC")) + timedelta(seconds=settings.auth_session_exp_seconds)
        return AuthenticationSession(session=session_value, exp=exp)
