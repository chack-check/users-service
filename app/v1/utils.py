import re
from dataclasses import fields

from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from .exceptions import (
    AuthRequired,
    UserWithThisEmailAlreadyExists,
    UserWithThisPhoneAlreadyExists,
    UserWithThisUsernameAlreadyExists,
)
from .schemas import DbUser


def validate_user_required(user: DbUser | None) -> None:
    if not user:
        raise AuthRequired()


def get_schema_from_pydantic(schema, model: BaseModel):
    include_fields = {field.name for field in fields(schema)}
    return schema(**model.model_dump(include=include_fields))


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
