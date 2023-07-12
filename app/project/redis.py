from redis.asyncio import Redis, ConnectionPool

from .settings import settings


pool = ConnectionPool.from_url(settings.redis_url)

redis_db = Redis(connection_pool=pool)
