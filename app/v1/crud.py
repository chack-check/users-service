import re
from dataclasses import asdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import insert, select, or_

from .graphql.graph_types import AuthData
from .schemas import DbUser
from .models import User
from .exceptions import (
    UserWithThisEmailAlreadyExists,
    UserWithThisPhoneAlreadyExists,
    UserWithThisUsernameAlreadyExists,
    UserDoesNotExist,
)


def handle_unique_violation(func):

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            field_name = re.search(r"\((.*)\)=\(.*\)", e.args[0]).group(1)
            exception = {
                'username': UserWithThisUsernameAlreadyExists,
                'phone': UserWithThisPhoneAlreadyExists,
                'email': UserWithThisEmailAlreadyExists,
            }[field_name]
            raise exception

    return wrapper


class UsersQueries:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, id: int | None = None,
                  phone_or_username: str | None = None) -> DbUser:
        stmt = select(User).where(or_(User.phone == phone_or_username,
                                      User.username == phone_or_username))
        result = await self._session.execute(stmt)
        db_users = result.fetchone()
        if not db_users:
            raise UserDoesNotExist

        return DbUser.model_validate(db_users[0])

    @handle_unique_violation
    async def create(self, user_data: AuthData, password: str) -> DbUser:
        values = asdict(user_data)
        values['password'] = password
        del values['password_repeat']
        stmt = insert(User).returning(User).values(**values)
        result = await self._session.execute(stmt)
        return DbUser.model_validate(result.fetchone()[0])
