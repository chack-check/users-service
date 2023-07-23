import random

from app.project.settings import settings
from app.project.redis import redis_db
from app.v1.exceptions import (
    VerificationAttemptsExpired,
    IncorrectVerificationCode,
)


class Verificator:

    def _get_verification_key(self, email_or_phone: str) -> str:
        return f"verification:{email_or_phone}"

    def _get_verification_attempts_key(self, email_or_phone: str) -> str:
        return f"verification:{email_or_phone}:attempts"

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
