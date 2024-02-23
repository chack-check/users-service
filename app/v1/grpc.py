import grpc
from grpc import aio

from app.project.db import session
from app.project.redis import redis_db
from app.protobuf import users_pb2_grpc

from .crud import UsersQueries
from .exceptions import IncorrectToken, UserDoesNotExist
from .factories import UserFactory
from .services.users import UsersSet


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
            return UserFactory.get_grpc_from_db_user(db_user)

    @handle_doesnt_exist_user
    async def GetUserByToken(self, request, context):
        async with session() as s:
            users_set = UsersSet(s, redis_db)
            db_user = await users_set.get_from_token(
                request.token, raise_exception=True
            )
            assert db_user
            return UserFactory.get_grpc_from_db_user(db_user)

    @handle_doesnt_exist_user
    async def GetUserByRefreshToken(self, request, context):
        async with session() as s:
            users_set = UsersSet(s, redis_db)
            db_user = await users_set.get_from_refresh_token(
                request.token, raise_exception=True
            )
            assert db_user
            return UserFactory.get_grpc_from_db_user(db_user)


async def start_server():
    server = aio.server()
    users_pb2_grpc.add_UsersServicer_to_server(Users(), server)
    listen_addr = '[::]:9090'
    server.add_insecure_port(listen_addr)
    await server.start()
    await server.wait_for_termination()
