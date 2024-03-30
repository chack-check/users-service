import datetime
import json
import logging
from typing import Literal

from jose import JWTError, jwt

from app.project.settings import settings

from ..exceptions import IncorrectToken
from ..schemas import DbUser

ACCESS_TOKEN_EXP_DELTA = datetime.timedelta(days=1)

REFRESH_TOKEN_EXP_DELTA = datetime.timedelta(days=30)

ALGORITHM = 'HS256'

logger = logging.getLogger("uvicorn.error")


class TokensSet:

    def _get_exp_delta(
            self, mode: Literal['refresh', 'access']
    ) -> datetime.timedelta:
        if mode == 'access':
            return ACCESS_TOKEN_EXP_DELTA

        return REFRESH_TOKEN_EXP_DELTA

    def create_token(self, user: DbUser,
                     mode: Literal['refresh', 'access']) -> str:
        logger.debug(f"Creating token: {user=} {mode=}")
        exp_delta = self._get_exp_delta(mode)
        exp = datetime.datetime.now(datetime.timezone.utc) + exp_delta
        token_sub = {'user_id': user.id, 'username': user.username}
        token_sub_json = json.dumps(token_sub)
        encode_data = {'sub': token_sub_json, 'exp': exp}
        logger.debug(f"Created token data: {encode_data}")
        return jwt.encode(encode_data, settings.secret_key, ALGORITHM)

    def decode_token(self, token: str) -> int:
        logger.debug(f"Decoding token")
        try:
            payload = jwt.decode(token, settings.secret_key,
                                 algorithms=[ALGORITHM])
            logger.debug(f"Decoded token payload: {payload}")
            if not payload['exp'] > datetime.datetime.now(datetime.timezone.utc).timestamp():
                logger.warning(f"Token expired")
                raise IncorrectToken

            decoded_sub = json.loads(payload['sub'])
            if "user_id" not in decoded_sub:
                logger.error(f"User id not in token subject {decoded_sub=}")
                raise IncorrectToken

            return decoded_sub['user_id']
        except (KeyError, JWTError) as e:
            logger.exception(e)
            raise IncorrectToken
