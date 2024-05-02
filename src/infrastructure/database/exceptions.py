from infrastructure.exceptions import BaseInfrastructureException


class BaseDatabaseException(BaseInfrastructureException): ...


class IncorrectFileSignature(BaseInfrastructureException): ...


class SessionNotFetchedException(BaseDatabaseException): ...
