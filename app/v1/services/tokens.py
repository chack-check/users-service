from typing import Literal
import datetime

from jose import jwt

from ..schemas import DbUser
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
        encode_data = {'user_id': user.id, 'exp': exp}
        return jwt.encode(encode_data, settings.secret_key, ALGORITHM)

    def verify_token(self, user: DbUser, token: str) -> bool:
        ...
