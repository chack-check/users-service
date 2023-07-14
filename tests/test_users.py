import pytest
from sqlalchemy import select

from app.v1.services.users import UsersSet
from app.v1.models import User
from app.v1.exceptions import (
    PasswordsNotMatch,
    UserWithThisEmailAlreadyExists,
    UserWithThisUsernameAlreadyExists,
    UserWithThisPhoneAlreadyExists,
)
from .base import (
    AUTH_USER_DATA,
    AUTH_USER_DATA_INVALID_PASSWORDS,
    AUTH_USER_DATA_EXISTS_EMAIL,
    AUTH_USER_DATA_EXISTS_USERNAME,
    AUTH_USER_DATA_EXISTS_PHONE,
)


@pytest.mark.asyncio
async def test_authenticate_valid_user(users_set: UsersSet):
    tokens = await users_set.authenticate(AUTH_USER_DATA)
    stmt = select(User.username)
    result = await users_set._users_queries._session.execute(stmt)
    db_users = result.fetchall()

    assert len(db_users) == 1
    assert db_users[0][0] == AUTH_USER_DATA.username
    assert tokens.access_token
    assert tokens.refresh_token


@pytest.mark.asyncio
async def test_authenticate_user_with_invalid_passwords(users_set: UsersSet):
    with pytest.raises(PasswordsNotMatch):
        await users_set.authenticate(AUTH_USER_DATA_INVALID_PASSWORDS)


@pytest.mark.asyncio
async def test_authenticate_already_exists_email(users_set: UsersSet):
    await users_set.authenticate(AUTH_USER_DATA)
    with pytest.raises(UserWithThisEmailAlreadyExists):
        await users_set.authenticate(AUTH_USER_DATA_EXISTS_EMAIL)


@pytest.mark.asyncio
async def test_authenticate_already_exists_username(users_set: UsersSet):
    await users_set.authenticate(AUTH_USER_DATA)
    with pytest.raises(UserWithThisUsernameAlreadyExists):
        await users_set.authenticate(AUTH_USER_DATA_EXISTS_USERNAME)


@pytest.mark.asyncio
async def test_authenticate_already_exists_phone(users_set: UsersSet):
    await users_set.authenticate(AUTH_USER_DATA)
    with pytest.raises(UserWithThisPhoneAlreadyExists):
        await users_set.authenticate(AUTH_USER_DATA_EXISTS_PHONE)
