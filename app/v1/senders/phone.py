from .base import BaseSender


class PhoneSender(BaseSender):

    def send_verification_code(self, to: list[str], code: str):
        raise NotImplementedError
