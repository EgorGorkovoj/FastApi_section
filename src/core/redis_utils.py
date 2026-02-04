from datetime import datetime, timedelta

import redis.asyncio as redis
from fastapi import Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from core.config import Config, settings
from core.logger import logger


class RedisManager:
    def __init__(self, settings: Config):
        self._settings = settings
        self._client: redis.Redis | None = None

    async def connect(self) -> redis.Redis:
        """
        Инициализирует и возвращает подключение к Redis.

        Возвращает:
            redis.Redis: Асинхронный клиент Redis.

        Исключения:
            Любое исключение при подключении пробрасывается дальше.
        """
        if self._client:
            return self._client

        self._client = redis.Redis(
            host=self._settings.REDIS_HOST,
            port=self._settings.REDIS_PORT,
            db=0,
            # decode_responses=True,
        )

        try:
            await self._client.ping()
            logger.info('Успешное подключение к Redis!')
            return self._client
        except Exception as e:
            logger.warning(f'Не удалось подключиться к Redis: {e}')
            raise

    async def disconnect_redis(self) -> None:
        """
        Закрывает соединение с Redis.
        """
        if self._client:
            await self._client.close()
            logger.info('Отключено от Redis.')
            self._client = None


redis_manager = RedisManager(settings=settings)


async def get_redis(redis_manager: RedisManager) -> redis.Redis:
    return await redis_manager.connect()


class RedisCacheManager:
    def __init__(self, redis_manager: RedisManager, settings: Config):
        self._redis_manager = redis_manager
        self._settings = settings

    async def init_fastapi_cache(self) -> None:
        try:
            redis_client = await self._redis_manager.connect()
            FastAPICache.init(
                RedisBackend(redis_client),
                prefix='fastapi-cache',
            )
            logger.info('FastAPI-Cache успешно инициализирован!')
        except Exception as e:
            logger.error(f'Не удалось инициализировать FastAPI-Cache: {e}')
            raise

    def calculate_ttl_until_reset(self) -> int:
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
            self._settings.cache_reset_time_obj,
        )

        if now >= target:
            target += timedelta(days=1)

        return int((target - now).total_seconds())

    def build_key_from_request(
        self,
        func,
        namespace: str = '',
        request: Request | None = None,
        *args,
        **kwargs,
    ) -> str:
        """
        Формирует ключ кэша на основе query-параметров запроса.

        Аргументы:
            func (Callable): Функция, для которой строится ключ.
            namespace (str): Пространство имён для ключа.
            request (Request | None): FastAPI запрос, откуда берутся query-параметры.

        Возвращает:
            str: Сформированный ключ кэша.
        """

        prefix = FastAPICache.get_prefix()

        if not request:
            return f'{prefix}:{namespace}'

        query = sorted(request.query_params.items())
        query_str = ':'.join(v for _, v in query)
        return f'{prefix}:{namespace}:{query_str}'


def redis_fastapi_cache(settings: Config, redis_manager: RedisManager) -> RedisCacheManager:
    cache_manager = RedisCacheManager(redis_manager=redis_manager, settings=settings)
    return cache_manager


redis_cache = redis_fastapi_cache(settings=settings, redis_manager=redis_manager)
