import logging

from .base import BaseSender

logger = logging.getLogger("uvicorn.error")


class PhoneSender(BaseSender):

    def send_verification_code(self, to: list[str], code: str):
        logger.debug(f"Sending verification code on phone {to=} {code=}")
        raise NotImplementedError
