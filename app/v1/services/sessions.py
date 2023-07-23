from redis.asyncio import Redis


class SessionSet:

    def __init__(self, redis_db: Redis):
        self.redis_db = redis_db

    async def has_user_session(self, user_id: int, refresh_token: str) -> bool:
        sessions_key = self._get_user_sessions_key(user_id)
        return await self.redis_db.sismember(sessions_key, refresh_token)

    def _get_user_sessions_key(self, user_id: int) -> str:
        return f"sessions:{user_id}"

    async def create(self, user_id: int, refresh_token: str):
        sessions_key = self._get_user_sessions_key(user_id)
        await self.redis_db.sadd(sessions_key, refresh_token)

    async def delete(self, user_id: int, refresh_token: str) -> str:
        ...

    async def delete_all(self, user_id: int) -> str:
        ...
