from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / '.env',
                                      env_prefix='USERS_SERVICE_')

    database_url: str
    redis_url: str
    secret_key: str


settings = Settings()
