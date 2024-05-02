from typing import Type

import grpc
from grpc import aio

from domain.sessions.exceptions import IncorrectTokenException
from domain.users.exceptions import UserNotFound
from infrastructure.database.exceptions import SessionNotFetchedException
from infrastructure.dependencies import (
    use_files_adapter,
    use_get_user_by_refresh_token_handler,
    use_get_user_by_token_handler,
    use_get_user_handler,
    use_get_users_by_ids_handler,
    use_session,
    use_sessions_storage_adapter,
    use_tokens_adapter,
    use_users_adapter,
)
from infrastructure.grpc_server.factories import UserProtoFactory

from .usersprotobuf import users_pb2, users_pb2_grpc


def handle_exception(exception: Type[Exception], status_code: grpc.StatusCode, details: str):

    def decorator(func):

        async def wrapper(self, request, context):
            try:
                return await func(self, request, context)
            except exception as e:
                context.set_code(status_code)
                context.set_details(details)
                raise

        return wrapper

    return decorator


class Users(users_pb2_grpc.UsersServicer):

    @handle_exception(exception=Exception, status_code=grpc.StatusCode.INTERNAL, details="Internal server error")
    @handle_exception(
        exception=IncorrectTokenException, status_code=grpc.StatusCode.UNAUTHENTICATED, details="Incorrect token"
    )
    @handle_exception(exception=UserNotFound, status_code=grpc.StatusCode.NOT_FOUND, details="User not found")
    async def GetUserById(self, request: users_pb2.GetUserByIdRequest, context) -> users_pb2.UserResponse:
        async for session in use_session():
            handler = use_get_user_handler(use_users_adapter(session), use_files_adapter(session))
            user = await handler.execute(id_=request.id)
            return UserProtoFactory.proto_from_domain(user)

        raise SessionNotFetchedException("error fetching session")

    @handle_exception(exception=Exception, status_code=grpc.StatusCode.INTERNAL, details="Internal server error")
    @handle_exception(
        exception=IncorrectTokenException, status_code=grpc.StatusCode.UNAUTHENTICATED, details="Incorrect token"
    )
    async def GetUsersByIds(self, request: users_pb2.GetUsersByIdsRequest, context) -> users_pb2.UsersArrayResponse:
        async for session in use_session():
            handler = use_get_users_by_ids_handler(use_users_adapter(session), use_files_adapter(session))
            users = await handler.execute(list(request.ids))
            return users_pb2.UsersArrayResponse(users=[UserProtoFactory.proto_from_domain(user) for user in users])

        raise SessionNotFetchedException("error fetching session")

    @handle_exception(exception=Exception, status_code=grpc.StatusCode.INTERNAL, details="Internal server error")
    @handle_exception(
        exception=IncorrectTokenException, status_code=grpc.StatusCode.UNAUTHENTICATED, details="Incorrect token"
    )
    @handle_exception(exception=UserNotFound, status_code=grpc.StatusCode.NOT_FOUND, details="User not found")
    async def GetUserByUsername(self, request: users_pb2.GetUserByUsernameRequest, context) -> users_pb2.UserResponse:
        async for session in use_session():
            handler = use_get_user_handler(use_users_adapter(session), use_files_adapter(session))
            user = await handler.execute(username=request.username)
            return UserProtoFactory.proto_from_domain(user)

        raise SessionNotFetchedException("error fetching session")

    @handle_exception(exception=Exception, status_code=grpc.StatusCode.INTERNAL, details="Internal server error")
    @handle_exception(
        exception=IncorrectTokenException, status_code=grpc.StatusCode.UNAUTHENTICATED, details="Incorrect token"
    )
    @handle_exception(exception=UserNotFound, status_code=grpc.StatusCode.NOT_FOUND, details="User not found")
    async def GetUserByEmail(self, request: users_pb2.GetUserByEmailRequest, context) -> users_pb2.UserResponse:
        async for session in use_session():
            handler = use_get_user_handler(use_users_adapter(session), use_files_adapter(session))
            user = await handler.execute(email=request.email)
            return UserProtoFactory.proto_from_domain(user)

        raise SessionNotFetchedException("error fetching session")

    @handle_exception(exception=Exception, status_code=grpc.StatusCode.INTERNAL, details="Internal server error")
    @handle_exception(
        exception=IncorrectTokenException, status_code=grpc.StatusCode.UNAUTHENTICATED, details="Incorrect token"
    )
    @handle_exception(exception=UserNotFound, status_code=grpc.StatusCode.NOT_FOUND, details="User not found")
    async def GetUserByToken(self, request: users_pb2.GetUserByTokenRequest, context) -> users_pb2.UserResponse:
        async for session in use_session():
            handler = use_get_user_by_token_handler(
                use_users_adapter(session), use_tokens_adapter(), use_files_adapter(session)
            )
            user = await handler.execute(request.token)
            return UserProtoFactory.proto_from_domain(user)

        raise SessionNotFetchedException("error fetching session")

    @handle_exception(exception=Exception, status_code=grpc.StatusCode.INTERNAL, details="Internal server error")
    @handle_exception(
        exception=IncorrectTokenException, status_code=grpc.StatusCode.UNAUTHENTICATED, details="Incorrect token"
    )
    @handle_exception(exception=UserNotFound, status_code=grpc.StatusCode.NOT_FOUND, details="User not found")
    async def GetUserByRefreshToken(self, request: users_pb2.GetUserByTokenRequest, context) -> users_pb2.UserResponse:
        async for session in use_session():
            handler = use_get_user_by_refresh_token_handler(
                use_users_adapter(session),
                use_tokens_adapter(),
                use_sessions_storage_adapter(),
                use_files_adapter(session),
            )
            user = await handler.execute(request.token)
            return UserProtoFactory.proto_from_domain(user)

        raise SessionNotFetchedException("error fetching session")


async def start_server():
    server = aio.server()
    users_pb2_grpc.add_UsersServicer_to_server(Users(), server)
    listen_addr = "[::]:9090"
    server.add_insecure_port(listen_addr)
    await server.start()
    await server.wait_for_termination()
