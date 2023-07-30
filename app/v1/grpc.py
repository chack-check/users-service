import grpc
from grpc import aio

from app.protobuf import users_pb2_grpc
from app.protobuf import users_pb2
from app.project.db import session
from app.project.redis import redis_db
from .crud import UsersQueries
from .services.users import UsersSet
from .schemas import DbUser
from .exceptions import (
    IncorrectToken,
    UserDoesNotExist,
)


def get_user_from_pydantic(user: DbUser):
    return users_pb2.UserResponse(
        id=user.id,
        username=user.username,
        phone=user.phone,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name,
        activity=user.activity,
        status=user.status,
        email_confirmed=user.email_confirmed,
        phone_confirmed=user.phone_confirmed,
        last_seen=user.last_seen.isoformat(),
    )


def handle_doesnt_exist_user(func):

    async def wrapper(self, request, context):
        try:
            return await func(self, request, context)
        except (UserDoesNotExist, IncorrectToken):
            context.abort(grpc.StatusCode.NOT_FOUND, "User doesn't exist")
            raise

    return wrapper


class Users(users_pb2_grpc.UsersServicer):

    @handle_doesnt_exist_user
    async def GetUserById(self, request, context):
        async with session() as s:
            users_queries = UsersQueries(s)
            db_user = await users_queries.get_by_id(request.id)
            return get_user_from_pydantic(db_user)

    @handle_doesnt_exist_user
    async def GetUserByToken(self, request, context):
        async with session() as s:
            users_set = UsersSet(s, redis_db)
            db_user = await users_set.get_from_token(request.token)
            return get_user_from_pydantic(db_user)


async def start_server():
    server = aio.server()
    users_pb2_grpc.add_UsersServicer_to_server(Users(), server)
    listen_addr = '[::]:9090'
    server.add_insecure_port(listen_addr)
    await server.start()
    await server.wait_for_termination()
