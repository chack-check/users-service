from logging import getLogger

from domain.users.models import User
from domain.users.ports import UserEventsPort

from .factories import UserEventFactory
from .publisher import RabbitConnection

logger = getLogger("uvicorn.error")


class UserEventsLoggingAdapter(UserEventsPort):

    def __init__(self, adapter: UserEventsPort):
        self._adapter = adapter

    async def send_user_created(self, user: User) -> None:
        logger.debug(f"sending user created event: {user=}")
        try:
            await self._adapter.send_user_created(user)
        except Exception as e:
            logger.exception(e)
            raise e

        logger.debug(f"user created event sended")

    async def send_user_changed(self, user: User) -> None:
        logger.debug(f"sending user changed event: {user=}")
        try:
            await self._adapter.send_user_changed(user)
        except Exception as e:
            logger.exception(e)
            raise e

        logger.debug(f"user changed event sended")


class UserEventsAdapter(UserEventsPort):

    def __init__(self, conn: RabbitConnection):
        self._connection = conn

    async def send_user_created(self, user: User) -> None:
        event = UserEventFactory.event_from_model(user, "user_created")
        await self._connection.send_message(event.model_dump_json().encode())

    async def send_user_changed(self, user: User) -> None:
        event = UserEventFactory.event_from_model(user, "user_changed")
        await self._connection.send_message(event.model_dump_json().encode())
