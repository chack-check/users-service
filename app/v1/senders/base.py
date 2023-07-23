from abc import ABC, abstractmethod


class BaseSender(ABC):

    @abstractmethod
    def send_verification_code(self, to: list[str], code: str):
        ...
