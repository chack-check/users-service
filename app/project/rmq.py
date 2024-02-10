import orjson
from typing import Any

import aio_pika

from app.project.settings import settings
from app.v1.schemas import DbUser


class RabbitConnection:

    def __init__(self, host: str,
                 queue_name: str):
        self._host = host
        self._queue_name = queue_name
        self._connection: aio_pika.Connection | None = None

    async def connect(self) -> None:
        self._connection = await aio_pika.connect(self._host)

    async def send_message(self, message: bytes):
        if not self._connection or self._connection.is_closed:
            await self.connect()

        async with self._connection:
            channel = await self._connection.channel()
            await channel.declare_queue(self._queue_name)
            await channel.default_exchange.publish(
                aio_pika.Message(body=message),
                routing_key=self._queue_name
            )


def get_user_created_message(user: DbUser) -> dict[str, Any]:
    return orjson.dumps({
        "event_type": "user_created",
        "data": user.model_dump(),
    })


connection = RabbitConnection(settings.publisher_rabbit_host, settings.publisher_rabbit_queue_name)
