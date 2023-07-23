from fastapi.templating import Jinja2Templates
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / '.env',
                                      env_prefix='USERS_SERVICE_')

    database_url: str
    redis_url: str
    secret_key: str
    allow_origins: list[str] = ['*']
    smtp_host: str
    smtp_port: str
    smtp_from: str
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = False
    verification_exp_seconds: int = 10 * 60  # 10 minutes
    verification_attempts_count: int = 7


settings = Settings()

templates_loader = Jinja2Templates(BASE_DIR / 'templates')
