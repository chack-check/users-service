from datetime import datetime, timedelta
import hmac
import hashlib
import random
import string

from app.project.settings import settings
from app.project.redis import redis_db
from app.v1.exceptions import (
    VerificationAttemptsExpired,
    IncorrectVerificationCode,
    IncorrectSignature,
    IncorrectAuthenticationSession,
)
from app.v1.schemas import AuthenticationSession


def verify_signature(phone_or_email: str, signature: str):
    generated_signature = hmac.new(
        settings.secret_key.encode(), phone_or_email.encode(), hashlib.sha256
    ).hexdigest()
    if generated_signature != signature:
        raise IncorrectSignature


class Verificator:

    def _get_verification_key(self, email_or_phone: str) -> str:
        return f"verification:{email_or_phone}"

    def _get_verification_attempts_key(self, email_or_phone: str) -> str:
        return f"verification:{email_or_phone}:attempts"

    def _get_session_key(self, email_or_phone: str) -> str:
        return f"authsession:{email_or_phone}"

    async def create_verification_code(self, email_or_phone: str) -> str:
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        key = self._get_verification_key(email_or_phone)
        await redis_db.setex(key, settings.verification_exp_seconds, code)
        attempts_key = self._get_verification_attempts_key(email_or_phone)
        await redis_db.setex(
            attempts_key, settings.verification_exp_seconds, 0
        )
        return code

    async def _increment_attempts(self, email_or_phone: str) -> None:
        key = self._get_verification_attempts_key(email_or_phone)
        await redis_db.incr(key)

    async def _validate_attempts(self, email_or_phone: str) -> None:
        await self._increment_attempts(email_or_phone)
        attempts_key = self._get_verification_attempts_key(email_or_phone)
        attempts = await redis_db.get(attempts_key)
        if attempts and int(attempts) > settings.verification_attempts_count:
            raise VerificationAttemptsExpired

    async def verify_code(self, email_or_phone: str, code: str) -> None:
        await self._validate_attempts(email_or_phone)
        key = self._get_verification_key(email_or_phone)
        right_code = await redis_db.get(key)
        if not right_code or right_code.decode() != code:
            raise IncorrectVerificationCode

    def _generate_session(self) -> str:
        return ''.join(random.choice(string.hexdigits) for _ in range(32))

    async def get_authentication_session(self, email_or_phone: str) -> AuthenticationSession:
        session_key = self._get_session_key(email_or_phone)
        session_value = self._generate_session()
        await redis_db.setex(session_key, settings.auth_session_exp_seconds, session_value)
        exp = datetime.utcnow() + timedelta(seconds=settings.auth_session_exp_seconds)
        return AuthenticationSession(session=session_value, exp=exp)

    async def verify_auth_session(self, email_or_phone: str, session: str) -> None:
        session_key = self._get_session_key(email_or_phone)
        right_session = await redis_db.get(session_key)
        if not right_session or right_session.decode() != session:
            raise IncorrectAuthenticationSession
