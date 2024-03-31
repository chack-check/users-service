import logging

import grpc
from grpc import aio

from app.project.db import session
from app.project.redis import redis_db
from app.protobuf import users_pb2, users_pb2_grpc

from .crud import UsersQueries
from .exceptions import IncorrectToken, UserDoesNotExist
from .factories import UserFactory
from .services.users import UsersSet

logger = logging.getLogger("uvicorn.error")


def handle_doesnt_exist_user(func):

    async def wrapper(self, request, context):
        try:
            return await func(self, request, context)
        except (UserDoesNotExist, IncorrectToken) as e:
            logger.exception(e)
            context.abort(grpc.StatusCode.NOT_FOUND, "User doesn't exist")
            raise

    return wrapper


class Users(users_pb2_grpc.UsersServicer):

    @handle_doesnt_exist_user
    async def GetUserById(self, request, context):
        logger.debug(f"Fetching user by id: grpc {request=}")
        async with session() as s:
            users_queries = UsersQueries(s)
            db_user = await users_queries.get_by_id(request.id)
            logger.debug(f"Fetched by id grpc user: {db_user=}")
            return UserFactory.get_grpc_from_db_user(db_user)

    async def GetUsersByIds(self, request, context):
        logger.debug(f"Fetching users by ids: {request=}")
        async with session() as s:
            users_queries = UsersQueries(s)
            db_users = await users_queries.get_by_ids(request.ids)
            logger.debug(f"Fetched by ids grpc users count: {len(db_users)}")
            return users_pb2.UsersArrayResponse(users=[UserFactory.get_grpc_from_db_user(user) for user in db_users])

    @handle_doesnt_exist_user
    async def GetUserByToken(self, request, context):
        logger.debug(f"Fetching user by token {request=}")
        async with session() as s:
            users_set = UsersSet(s, redis_db)
            db_user = await users_set.get_from_token(
                request.token, raise_exception=True
            )
            logger.debug(f"Fetched user by token: {db_user=}")
            if not db_user:
                logger.warning("User not found for token")
                context.abort(grpc.StatusCode.NOT_FOUND, "User doesn't exist")
                return

            return UserFactory.get_grpc_from_db_user(db_user)

    @handle_doesnt_exist_user
    async def GetUserByRefreshToken(self, request, context):
        logger.debug("Fetching user by refresh token")
        async with session() as s:
            users_set = UsersSet(s, redis_db)
            db_user = await users_set.get_from_refresh_token(
                request.token, raise_exception=True
            )
            logger.debug(f"Fetched user by refresh token: {db_user=}")
            if not db_user:
                logger.warning("User not found by refresh token")
                context.abort(grpc.StatusCode.NOT_FOUND, "User doesn't exist")
                return

            return UserFactory.get_grpc_from_db_user(db_user)


async def start_server():
    logger.debug("Starting grpc server")
    server = aio.server()
    users_pb2_grpc.add_UsersServicer_to_server(Users(), server)
    listen_addr = '[::]:9090'
    server.add_insecure_port(listen_addr)
    await server.start()
    await server.wait_for_termination()
