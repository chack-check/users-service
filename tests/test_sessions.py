import pytest

from app.v1.services.sessions import SessionSet
from app.project.redis import redis_db


@pytest.mark.asyncio
async def test_create_session(session_set: SessionSet):
    await session_set.create(50, 'sample_refresh_token')

    user_sessions = await redis_db.smembers('sessions:50')

    assert len(user_sessions) == 1
    assert user_sessions.pop().decode() == 'sample_refresh_token'


@pytest.mark.asyncio
async def test_create_already_exists_session(session_set: SessionSet):
    await session_set.create(1, 'sample_refresh_token')

    user_sessions = await redis_db.smembers('sessions:50')

    assert len(user_sessions) == 1
