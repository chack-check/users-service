import datetime
import json
from typing import Literal

from jose import JWTError, jwt

from app.project.settings import settings

from ..exceptions import IncorrectToken
from ..schemas import DbUser

ACCESS_TOKEN_EXP_DELTA = datetime.timedelta(days=1)

REFRESH_TOKEN_EXP_DELTA = datetime.timedelta(days=30)

ALGORITHM = 'HS256'


class TokensSet:

    def _get_exp_delta(
            self, mode: Literal['refresh', 'access']
    ) -> datetime.timedelta:
        if mode == 'access':
            return ACCESS_TOKEN_EXP_DELTA

        return REFRESH_TOKEN_EXP_DELTA

    def create_token(self, user: DbUser,
                     mode: Literal['refresh', 'access']) -> str:
        exp_delta = self._get_exp_delta(mode)
        exp = datetime.datetime.now(datetime.timezone.utc) + exp_delta
        token_sub = {'user_id': user.id, 'username': user.username}
        token_sub_json = json.dumps(token_sub)
        encode_data = {'sub': token_sub_json, 'exp': exp}
        return jwt.encode(encode_data, settings.secret_key, ALGORITHM)

    def decode_token(self, token: str) -> int:
        try:
            payload = jwt.decode(token, settings.secret_key,
                                 algorithms=[ALGORITHM])
            if not payload['exp'] > datetime.datetime.now(datetime.timezone.utc).timestamp():
                raise IncorrectToken

            decoded_sub = json.loads(payload['sub'])
            if not "user_id" in decoded_sub:
                raise IncorrectToken

            return decoded_sub['user_id']
        except (KeyError, JWTError):
            raise IncorrectToken
