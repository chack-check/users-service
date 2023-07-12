import  re
from dataclasses import asdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import insert

from .graphql.types import AuthData
from .schemas import DbUser
from .models import User
from .exceptions import (
    UserWithThisEmailAlreadyExists,
    UserWithThisPhoneAlreadyExists,
    UserWithThisUsernameAlreadyExists,
)


def handle_unique_violation(func):

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            field_name = re.search(r"\((.*)\)=\(.*\)", e.args[0]).group(1)
            exception = {
                'username': UserWithThisUsernameAlreadyExists("User with this username alaready exists"),
                'phone': UserWithThisPhoneAlreadyExists("User with this phone already exists"),
                'email': UserWithThisEmailAlreadyExists("User with this email already exists"),
            }[field_name]
            raise exception

    return wrapper


class UsersQueries:

    def __init__(self, session: AsyncSession):
        self._session = session

    @handle_unique_violation
    async def create(self, user_data: AuthData, password: str) -> DbUser:
        values = asdict(user_data)
        values['password'] = password
        del values['password_repeat']
        stmt = insert(User).returning(User).values(**values)
        result = await self._session.execute(stmt)
        return DbUser.model_validate(result.fetchone()[0])
