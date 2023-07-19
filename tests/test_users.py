import math
from dataclasses import asdict

import pytest
from sqlalchemy import select, insert

from app.v1.services.users import UsersSet, pwd_context
from app.v1.models import User
from app.v1.exceptions import (
    PasswordsNotMatch,
    UserWithThisEmailAlreadyExists,
    UserWithThisUsernameAlreadyExists,
    UserWithThisPhoneAlreadyExists,
    UserDoesNotExist,
    IncorrectPassword,
    IncorrectToken,
)
from .base import (
    AUTH_USER_DATA,
    AUTH_USER_DATA_INVALID_PASSWORDS,
    AUTH_USER_DATA_EXISTS_EMAIL,
    AUTH_USER_DATA_EXISTS_USERNAME,
    AUTH_USER_DATA_EXISTS_PHONE,
    LOGIN_USER_DATA_INCORRECT_PASSWORD,
    LOGIN_USER_DATA_INCORRECT_USERNAME,
    LOGIN_USER_DATA_PHONE,
    LOGIN_USER_DATA_USERNAME,
    MANY_USERS_DATA,
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


@pytest.mark.asyncio
async def test_login_user_with_username(users_set: UsersSet):
    password_hash = pwd_context.hash(AUTH_USER_DATA.password)
    auth_dict = asdict(AUTH_USER_DATA)
    auth_dict['password'] = password_hash
    del auth_dict['password_repeat']
    stmt = insert(User).values(**auth_dict)
    await users_set._users_queries._session.execute(stmt)

    tokens = await users_set.login(LOGIN_USER_DATA_USERNAME)

    assert tokens.access_token
    assert tokens.refresh_token


@pytest.mark.asyncio
async def test_login_user_with_phone(users_set: UsersSet):
    password_hash = pwd_context.hash(AUTH_USER_DATA.password)
    auth_dict = asdict(AUTH_USER_DATA)
    auth_dict['password'] = password_hash
    del auth_dict['password_repeat']
    stmt = insert(User).values(**auth_dict)
    await users_set._users_queries._session.execute(stmt)

    tokens = await users_set.login(LOGIN_USER_DATA_PHONE)

    assert tokens.access_token
    assert tokens.refresh_token


@pytest.mark.asyncio
async def test_login_user_incorrect_username_or_phone(users_set: UsersSet):
    password_hash = pwd_context.hash(AUTH_USER_DATA.password)
    auth_dict = asdict(AUTH_USER_DATA)
    auth_dict['password'] = password_hash
    del auth_dict['password_repeat']
    stmt = insert(User).values(**auth_dict)
    await users_set._users_queries._session.execute(stmt)

    with pytest.raises(UserDoesNotExist):
        await users_set.login(LOGIN_USER_DATA_INCORRECT_USERNAME)


@pytest.mark.asyncio
async def test_login_user_incorrect_password(users_set: UsersSet):
    password_hash = pwd_context.hash(AUTH_USER_DATA.password)
    auth_dict = asdict(AUTH_USER_DATA)
    auth_dict['password'] = password_hash
    del auth_dict['password_repeat']
    stmt = insert(User).values(**auth_dict)
    await users_set._users_queries._session.execute(stmt)

    with pytest.raises(IncorrectPassword):
        await users_set.login(LOGIN_USER_DATA_INCORRECT_PASSWORD)


@pytest.mark.asyncio
async def test_get_by_username(users_set: UsersSet):
    password_hash = pwd_context.hash(AUTH_USER_DATA.password)
    auth_dict = asdict(AUTH_USER_DATA)
    auth_dict['password'] = password_hash
    del auth_dict['password_repeat']
    stmt = insert(User).values(**auth_dict)
    await users_set._users_queries._session.execute(stmt)

    user = await users_set.get(username=AUTH_USER_DATA.username)
    assert user.username == AUTH_USER_DATA.username


@pytest.mark.asyncio
async def test_get_by_id(users_set: UsersSet):
    password_hash = pwd_context.hash(AUTH_USER_DATA.password)
    auth_dict = asdict(AUTH_USER_DATA)
    auth_dict['password'] = password_hash
    del auth_dict['password_repeat']
    stmt = insert(User).returning(User.id).values(**auth_dict)
    result = await users_set._users_queries._session.execute(stmt)
    id = result.fetchone()[0]

    user = await users_set.get(id=id)
    assert user.id == id


@pytest.mark.asyncio
async def test_get_by_email(users_set: UsersSet):
    password_hash = pwd_context.hash(AUTH_USER_DATA.password)
    auth_dict = asdict(AUTH_USER_DATA)
    auth_dict['password'] = password_hash
    del auth_dict['password_repeat']
    stmt = insert(User).values(**auth_dict)
    await users_set._users_queries._session.execute(stmt)

    user = await users_set.get(email=AUTH_USER_DATA.email)
    assert user.email == AUTH_USER_DATA.email


@pytest.mark.asyncio
async def test_get_by_phone(users_set: UsersSet):
    password_hash = pwd_context.hash(AUTH_USER_DATA.password)
    auth_dict = asdict(AUTH_USER_DATA)
    auth_dict['password'] = password_hash
    del auth_dict['password_repeat']
    stmt = insert(User).values(**auth_dict)
    await users_set._users_queries._session.execute(stmt)

    user = await users_set.get(phone=AUTH_USER_DATA.phone)
    assert user.phone == AUTH_USER_DATA.phone


@pytest.mark.asyncio
async def test_get_with_many_fields(users_set: UsersSet):
    with pytest.raises(AssertionError):
        await users_set.get(phone='phone', email='email')


@pytest.mark.asyncio
async def test_get_with_noone_field(users_set: UsersSet):
    with pytest.raises(AssertionError):
        await users_set.get()


@pytest.mark.asyncio
async def test_get_from_token(users_set: UsersSet):
    password_hash = pwd_context.hash(AUTH_USER_DATA.password)
    auth_dict = asdict(AUTH_USER_DATA)
    auth_dict['password'] = password_hash
    del auth_dict['password_repeat']
    stmt = insert(User).returning(User.id).values(**auth_dict)
    result = await users_set._users_queries._session.execute(stmt)
    id = result.fetchone()[0]

    tokens = await users_set.login(LOGIN_USER_DATA_USERNAME)

    user = await users_set.get_from_token(tokens.access_token)
    assert id == user.id


@pytest.mark.asyncio
async def test_get_from_token_with_incorrect_token_without_raise_exception(users_set: UsersSet):
    user_id = await users_set.get_from_token('incorrect_token', raise_exception=False)
    assert user_id is None


@pytest.mark.asyncio
async def test_get_from_token_with_incorrect_token_with_raise_exception(users_set: UsersSet):
    with pytest.raises(IncorrectToken):
        await users_set.get_from_token('incorrect_token', raise_exception=True)


@pytest.mark.asyncio
async def test_search_users(users_set: UsersSet):
    await users_set._users_queries._session.execute(insert(User), MANY_USERS_DATA)

    data = await users_set.search(query='ivan')

    assert data.page == 1
    assert data.per_page == 20
    assert data.num_pages == math.ceil(len(MANY_USERS_DATA) / 20)
    assert len(data.data) == 20


@pytest.mark.asyncio
async def test_search_users_with_page(users_set: UsersSet):
    await users_set._users_queries._session.execute(insert(User), MANY_USERS_DATA)

    data = await users_set.search(query='', page=2)

    assert data.page == 2
    assert data.per_page == 20
    assert data.num_pages == math.ceil(len(MANY_USERS_DATA) / 20)
    assert len(data.data) == 20
    assert data.data[0].username == 'test20'


@pytest.mark.asyncio
async def test_search_users_with_num_pages(users_set: UsersSet):
    await users_set._users_queries._session.execute(insert(User), MANY_USERS_DATA)

    data = await users_set.search(query='', per_page=50)

    assert data.page == 1
    assert data.per_page == 50
    assert data.num_pages == math.ceil(len(MANY_USERS_DATA) / 50)
    assert len(data.data) == 50


@pytest.mark.asyncio
async def test_search_concrete_user_by_first_name(users_set: UsersSet):
    await users_set._users_queries._session.execute(insert(User), MANY_USERS_DATA)

    data = await users_set.search(query='test39')

    assert data.page == 1
    assert data.per_page == 20
    assert data.num_pages == 1
    assert len(data.data) == 1
    assert data.data[0].username == 'test39'


@pytest.mark.asyncio
async def test_search_with_zero_page(users_set: UsersSet):
    await users_set._users_queries._session.execute(insert(User), MANY_USERS_DATA)

    data = await users_set.search(query='', page=0)

    assert data.page == 1
    assert data.per_page == 20
    assert data.num_pages == math.ceil(len(MANY_USERS_DATA) / 20)
    assert len(data.data) == 20


@pytest.mark.asyncio
async def test_search_with_incorrect_page(users_set: UsersSet):
    await users_set._users_queries._session.execute(insert(User), MANY_USERS_DATA)

    data = await users_set.search(query='', page=2931)

    assert data.page == 1
    assert data.per_page == 20
    assert data.num_pages == math.ceil(len(MANY_USERS_DATA) / 20)
    assert len(data.data) == 20
