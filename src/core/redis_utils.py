from datetime import datetime, time, timedelta

import redis.asyncio as redis
from fastapi import Request

from core.config import Config, settings
from core.logger import logger


async def create_redis(settings: Config) -> redis.Redis:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
        decode_responses=True,
    )
    try:
        await redis_client.ping()
        logger.info('Успешное подключение к Redis!')
        return redis_client
    except Exception as e:
        logger.warning(f'Не удалось подключиться к Redis: {e}')
        raise


def get_redis(request: Request) -> redis.Redis:
    return request.app.state.redis


class RedisCache:
    def __init__(self, redis_client: redis.Redis):
        self._redis_client = redis_client

    def build_key_from_request(self, request: Request, prefix: str = 'fastapi-cache') -> str:
        """
        Формирует ключ кэша на основе query-параметров запроса.

        Аргументы:
            func (Callable): Функция, для которой строится ключ.
            namespace (str): Пространство имён для ключа.
            request (Request | None): FastAPI запрос, откуда берутся query-параметры.

        Возвращает:
            str: Сформированный ключ кэша.
        """

        namespace = request.url.path.rstrip('/').split('/')[-1]

        query = sorted(request.query_params.items())
        query_str = ':'.join(v for _, v in query)
        return f'{prefix}:{namespace}:{query_str}'

    def calculate_ttl_until_reset(self, reset_time: time = settings.cache_reset_time_obj) -> int:
        """
        Вычисляет TTL (Time to Life) в секундах до указанного времени сегодня.
        Если текущее время уже прошло, TTL считается до этого времени завтра.

        Аргументы:
            target_time (time): Время, до которого считается TTL.

        Возвращает:
            int: Количество секунд.
        """
        now = datetime.now()
        target = datetime.combine(
            now.date(),
            reset_time,
        )

        if now >= target:
            target += timedelta(days=1)

        return int((target - now).total_seconds())

    async def get_key(self, request: Request) -> str | bytes | None:
        cache_key = self.build_key_from_request(request)
        return await self._redis_client.get(cache_key)

    async def set_key(self, request: Request, value_cache: str | bytes) -> None:
        cache_key = self.build_key_from_request(request)
        await self._redis_client.set(
            cache_key,
            value_cache,
            ex=self.calculate_ttl_until_reset(),
        )
