from typing import Literal
import datetime

from jose import jwt, JWTError

from ..schemas import DbUser
from ..exceptions import IncorrectToken
from app.project.settings import settings


ACCESS_TOKEN_EXP_DELTA = datetime.timedelta(minutes=30)

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
        exp = datetime.datetime.utcnow() + exp_delta
        token_sub = {'user_id': user.id, 'username': user.username}
        encode_data = {'sub': token_sub, 'exp': exp}
        return jwt.encode(encode_data, settings.secret_key, ALGORITHM)

    def decode_token(self, token: str) -> int:
        try:
            payload = jwt.decode(token, settings.secret_key,
                                 algorithms=[ALGORITHM])
            assert payload['exp'] > datetime.datetime.utcnow().timestamp()
            return payload['user_id']
        except (AssertionError, KeyError, JWTError):
            raise IncorrectToken
