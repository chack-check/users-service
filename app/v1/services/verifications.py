import hashlib
import hmac
import logging
import random
import string
from datetime import datetime, timedelta, timezone

from app.project.redis import redis_db
from app.project.settings import settings
from app.v1.exceptions import (
    IncorrectAuthenticationSession,
    IncorrectSignature,
    IncorrectVerificationCode,
    VerificationAttemptsExpired,
)
from app.v1.schemas import AuthenticationSession, SavingFileData, SavingFileObject

logger = logging.getLogger("uvicorn.error")


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
        logger.debug(f"Creating verification code for {email_or_phone=}")
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        logger.debug(f"Created verification code for {email_or_phone=} {code=}")
        key = self._get_verification_key(email_or_phone)
        logger.debug(f"Setting verification code {key=} {code=}")
        await redis_db.setex(key, settings.verification_exp_seconds, code)
        attempts_key = self._get_verification_attempts_key(email_or_phone)
        logger.debug(f"Setting verification code attempts {attempts_key=} {settings.verification_exp_seconds} initial value = 0")
        await redis_db.setex(
            attempts_key, settings.verification_exp_seconds, 0
        )
        return code

    async def _increment_attempts(self, email_or_phone: str) -> None:
        key = self._get_verification_attempts_key(email_or_phone)
        logger.debug(f"Incrementing attempts key for {key=}")
        await redis_db.incr(key)

    async def _validate_attempts(self, email_or_phone: str) -> None:
        logger.debug(f"Validating attempts for verification code {email_or_phone=}")
        await self._increment_attempts(email_or_phone)
        attempts_key = self._get_verification_attempts_key(email_or_phone)
        attempts = await redis_db.get(attempts_key)
        logger.debug(f"Attempts count {attempts_key=} {attempts=}")
        if attempts and int(attempts) > settings.verification_attempts_count:
            logger.warning(f"Attempts count is more than valid value {attempts} > {settings.verification_attempts_count}")
            raise VerificationAttemptsExpired

    async def verify_code(self, email_or_phone: str, code: str) -> None:
        logger.debug(f"Verifying code {email_or_phone=} {code=}")
        await self._validate_attempts(email_or_phone)
        key = self._get_verification_key(email_or_phone)
        right_code = await redis_db.get(key)
        logger.debug(f"Verify code {key=} {right_code=} {code=}")
        if not right_code or right_code.decode() != code:
            logger.debug(f"Code {code} for {email_or_phone=} is incorrect. Right value: {right_code}")
            raise IncorrectVerificationCode

    def _generate_session(self) -> str:
        return ''.join(random.choice(string.hexdigits) for _ in range(32))

    async def get_authentication_session(self, email_or_phone: str) -> AuthenticationSession:
        logger.debug(f"Generating authentication session for {email_or_phone=}")
        session_key = self._get_session_key(email_or_phone)
        session_value = self._generate_session()
        logger.debug(f"Generated session key: {session_key=} {session_value=} {email_or_phone=}")
        await redis_db.setex(session_key, settings.auth_session_exp_seconds, session_value)
        exp = datetime.now(timezone.utc) + timedelta(seconds=settings.auth_session_exp_seconds)
        logger.debug(f"Generated session {session_key=} {session_value=} {exp=}")
        return AuthenticationSession(session=session_value, exp=exp)

    async def verify_auth_session(self, email_or_phone: str, session: str) -> None:
        logger.debug(f"Verify auth session {email_or_phone=} {session=}")
        session_key = self._get_session_key(email_or_phone)
        right_session = await redis_db.get(session_key)
        logger.debug(f"Verify session {session_key=} {session=} {right_session=}")
        if not right_session or right_session.decode() != session:
            logger.warning(f"Authentication session is incorrect: {email_or_phone=} {session=} != {right_session=}")
            raise IncorrectAuthenticationSession

    async def clear_verifications(self, email_or_phone: str) -> None:
        logger.debug(f"Clear all verification information for {email_or_phone=}")
        session_key = self._get_session_key(email_or_phone)
        attempts_key = self._get_verification_attempts_key(email_or_phone)
        verification_key = self._get_verification_key(email_or_phone)
        await redis_db.delete(session_key, attempts_key, verification_key)

    def _verify_file_object(self, file_object: SavingFileObject) -> None:
        logger.debug(f"Verify file signature {file_object=}")
        file_signature = hmac.new(
            settings.files_signature_secret.encode(),
            (f"{file_object.filename}:{file_object.system_filetype.value}").encode(),
            hashlib.sha256
        ).hexdigest()
        logger.debug(f"Verify file object. Generated signature = {file_signature}. Files service signature = {file_object.signature}")
        if not file_signature == file_object.signature:
            raise IncorrectSignature

    def verify_file(self, file: SavingFileData) -> None:
        self._verify_file_object(file.original_file)
        if file.converted_file:
            self._verify_file_object(file.converted_file)
