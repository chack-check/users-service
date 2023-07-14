import datetime
import pytest
from jose import jwt

from .base import TOKEN_USER
from app.v1.services.tokens import (
    TokensSet, ALGORITHM, ACCESS_TOKEN_EXP_DELTA, REFRESH_TOKEN_EXP_DELTA
)
from app.project.settings import settings


@pytest.mark.asyncio
async def test_create_access_token(tokens_set: TokensSet):
    created_token = tokens_set.create_token(TOKEN_USER, mode='access')
    token_data = jwt.decode(created_token, settings.secret_key, algorithms=[ALGORITHM])

    assert 'user_id' in token_data
    assert 'exp' in token_data

    assert token_data['user_id'] == TOKEN_USER.id
    assert token_data['exp'] == int((datetime.datetime.utcnow() + ACCESS_TOKEN_EXP_DELTA).timestamp())


@pytest.mark.asyncio
async def test_create_refresh_token(tokens_set: TokensSet):
    created_token = tokens_set.create_token(TOKEN_USER, mode='refresh')
    token_data = jwt.decode(created_token, settings.secret_key, algorithms=[ALGORITHM])

    assert 'user_id' in token_data
    assert 'exp' in token_data

    assert token_data['user_id'] == TOKEN_USER.id
    assert token_data['exp'] == int((datetime.datetime.utcnow() + REFRESH_TOKEN_EXP_DELTA).timestamp())
