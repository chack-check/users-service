import datetime
import json
from logging import getLogger
from typing import Literal

from jose import JWTError, jwt

from domain.sessions.ports import TokensPort
from domain.users.models import User
from infrastructure.settings import settings

ACCESS_TOKEN_EXP_DELTA = datetime.timedelta(days=1)

REFRESH_TOKEN_EXP_DELTA = datetime.timedelta(days=30)

ALGORITHM = "HS256"

logger = getLogger("uvicorn.error")


class TokensLoggingAdapter(TokensPort):

    def __init__(self, adapter: TokensPort):
        self._adapter = adapter

    def create_token(self, user: User, type: Literal["access", "refresh"]) -> str:
        logger.info(f"creating token: {user=} {type=}")
        try:
            token = self._adapter.create_token(user, type)
        except Exception as e:
            logger.exception(e)
            raise

        logger.info(f"created token: {token=}")
        return token

    async def decode_token(self, token: str) -> int:
        logger.info(f"decoding token: {token=}")
        try:
            user_id = await self._adapter.decode_token(token)
        except Exception as e:
            logger.exception(e)
            raise

        logger.info(f"decoded token user id: {user_id=}")
        return user_id


class TokensAdapter(TokensPort):

    def _get_exp_delta(self, mode: Literal["refresh", "access"]) -> datetime.timedelta:
        if mode == "access":
            return ACCESS_TOKEN_EXP_DELTA

        return REFRESH_TOKEN_EXP_DELTA

    def create_token(self, user: User, type: Literal["access", "refresh"]) -> str:
        exp_delta = self._get_exp_delta(type)
        exp = datetime.datetime.now(datetime.timezone.utc) + exp_delta
        token_sub = {"user_id": user.get_id(), "username": user.get_username()}
        token_sub_json = json.dumps(token_sub)
        encode_data = {"sub": token_sub_json, "exp": exp}
        return jwt.encode(encode_data, settings.secret_key, ALGORITHM)

    async def decode_token(self, token: str) -> int:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
            if not payload["exp"] > datetime.datetime.now(datetime.timezone.utc).timestamp():
                return 0

            decoded_sub = json.loads(payload["sub"])
            if "user_id" not in decoded_sub:
                return 0

            return decoded_sub["user_id"]
        except (KeyError, JWTError):
            return 0
