import logging

import aio_pika
from aio_pika.abc import AbstractConnection

from app.project.settings import settings

logger = logging.getLogger(__file__)


class RabbitConnection:

    def __init__(self, host: str,
                 exchange_name: str):
        self._host = host
        self._exchange_name = exchange_name
        self._connection: AbstractConnection | None = None

    async def connect(self) -> None:
        self._connection = await aio_pika.connect(self._host)

    async def send_message(self, message: bytes):
        if not self._connection or self._connection.is_closed:
            await self.connect()

        assert self._connection
        async with self._connection:
            channel = await self._connection.channel()
            exchange = await channel.declare_exchange(self._exchange_name, aio_pika.ExchangeType.FANOUT, durable=True)
            logger.info(f"Sending event to rabbitmq: {message=}")
            await exchange.publish(
                aio_pika.Message(body=message, content_type="application/json"),
                routing_key=""
            )


class MockedConnection:

    def __init__(self, *args, **kwargs):
        ...

    async def connect(self) -> None:
        ...

    async def send_message(self, message: bytes):
        ...


if settings.run_mode == "test":
    connection = MockedConnection()
else:
    connection = RabbitConnection(settings.publisher_rabbit_host, settings.publisher_rabbit_exchange_name)
