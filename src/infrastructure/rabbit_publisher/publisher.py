import logging

import aio_pika
from aio_pika.abc import AbstractConnection

from infrastructure.settings import settings

logger = logging.getLogger("uvicorn.error")


class RabbitConnection:

    def __init__(self, host: str, exchange_name: str):
        self._host = host
        self._exchange_name = exchange_name
        self._connection: AbstractConnection | None = None

    async def connect(self) -> None:
        logger.debug(f"Connecting to rabbitmq host: {self._host}")
        self._connection = await aio_pika.connect_robust(self._host)

    async def send_message(self, message: bytes):
        if not self._connection or self._connection.is_closed:
            logger.warning(f"Reconnecting rabbitmq connection {self._connection=}")
            await self.connect()

        assert self._connection
        async with self._connection:
            channel = await self._connection.channel()
            logger.debug(f"Fetched rabbitmq connection channel {channel=}")
            exchange = await channel.declare_exchange(self._exchange_name, aio_pika.ExchangeType.FANOUT, durable=True)
            logger.debug(f"Declared rabbitmq exchange {exchange=} exchange_name={self._exchange_name}")
            logger.debug(f"Sending event to rabbitmq: {message=}")
            await exchange.publish(
                aio_pika.Message(body=message, content_type="application/json"), routing_key="", timeout=2
            )
            logger.debug(f"Sended event to rabbitmq: {message=}")


connection = RabbitConnection(settings.publisher_rabbit_host, settings.publisher_rabbit_exchange_name)
