from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    database_url: str
    model_config = SettingsConfigDict(env_file=BASE_DIR / '.env', env_prefix='USERS_SERVICE_')


settings = Settings()
