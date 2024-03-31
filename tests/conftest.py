import asyncio

import pytest
import pytest_asyncio

from app.project.db import session
from app.project.redis import redis_db
from app.v1.services.users import UsersSet
from app.v1.services.tokens import TokensSet
from app.v1.services.sessions import SessionSet
from app.v1.services.verifications import Verificator


@pytest.fixture
def session_set() -> SessionSet:
    return SessionSet(redis_db)


@pytest.fixture
def tokens_set() -> TokensSet:
    return TokensSet()


@pytest_asyncio.fixture
async def users_set() -> UsersSet:
    async with session() as s:
        users_set = UsersSet(s, redis_db)
        yield users_set
        await s.rollback()


@pytest.fixture
def verificator() -> Verificator:
    return Verificator()


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()