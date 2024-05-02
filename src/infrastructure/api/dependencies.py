from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from strawberry.fastapi import BaseContext

oauth2_scheme = HTTPBearer(auto_error=False)


class CustomContext(BaseContext):

    def __init__(
        self,
        token: str | None,
    ):
        self.token = token


def use_custom_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(oauth2_scheme)],
) -> CustomContext:
    return CustomContext(credentials.credentials if credentials else None)


async def get_context(context: Annotated[CustomContext, Depends(use_custom_context)]) -> CustomContext:
    return context
