import asyncio

import pytest
import pytest_asyncio

from app.project.db import session, init_db
from app.project.redis import redis_db
from app.v1.services.users import UsersSet
from app.v1.services.tokens import TokensSet
from app.v1.services.sessions import SessionSet


@pytest.fixture
def session_set() -> SessionSet:
    return SessionSet(redis_db)


@pytest.fixture
def tokens_set() -> TokensSet:
    return TokensSet()


@pytest_asyncio.fixture
async def users_set() -> UsersSet:
    await init_db()
    async with session() as s:
        users_set = UsersSet(s, redis_db)
        yield users_set
        await s.rollback()


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()