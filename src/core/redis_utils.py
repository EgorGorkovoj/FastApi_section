from datetime import datetime, timedelta

import redis.asyncio as redis
from fastapi import Request
from fastapi_cache import FastAPICache

from core.config import settings
from core.logger import logger


async def connect_redis() -> redis.Redis:
    """
    Инициализирует и возвращает подключение к Redis.

    Возвращает:
        redis.Redis: Асинхронный клиент Redis.

    Исключения:
        Любое исключение при подключении пробрасывается дальше.
    """

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


async def disconnect_redis(redis_client: redis.Redis) -> None:
    """
    Закрывает соединение с Redis.

    Аргументы:
        redis_client (redis.Redis): Клиент Redis.
    """
    if redis_client:
        await redis_client.close()
        logger.info('Отключено от Redis.')


def calculate_ttl_until() -> int:
    """
    Вычисляет TTL (Time to Life) в секундах до указанного времени сегодня.
    Если текущее время уже прошло, TTL считается до этого времени завтра.

    Аргументы:
        target_time (time): Время, до которого считается TTL.

    Возвращает:
        int: Количество секунд.
    """

    now = datetime.now()
    target = datetime.combine(now.date(), settings.cache_reset_time_obj)

    if now >= target:
        target = target + timedelta(days=1)

    delta = target - now
    return int(delta.total_seconds())


def build_cache_key_from_query(
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
