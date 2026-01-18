from dataclasses import dataclass
from datetime import time
from pathlib import Path
from dotenv import load_dotenv

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).parent.parent
DOWNLOADS_DIR = BASE_DIR / 'downloads'

load_dotenv()


@dataclass
class URLData:
    SITE_URL: str = 'https://spimex.com'
    PAGE_URL: str = f'{SITE_URL}/markets/oil_products/trades/results/'


class Config(BaseSettings):
    APP_TITLE: str
    APP_DESCRIPTION: str
    DB_TYPE: str
    DB_API: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    REDIS_HOST: str
    REDIS_PORT: str
    CACHE_RESET_TIME: str = '14:11'

    @property
    def cache_reset_time_obj(self) -> time:
        """Возвращает время сброса кэша как datetime.time"""
        hour, minute = map(int, self.CACHE_RESET_TIME.split(':'))
        return time(hour=hour, minute=minute)

    @property
    def database_url(self):
        return (
            f'{self.DB_TYPE}+{self.DB_API}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
            f'@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
        )

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Config()
url = URLData()
