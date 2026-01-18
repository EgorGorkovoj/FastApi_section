import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from api.v1.routers import main_router
from core.config import settings
from core.logger import LoggingMiddleware
from core.redis_utils import connect_redis, disconnect_redis
from services.check_data_parser import check_last_date_parser_spmx


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = await connect_redis()
    FastAPICache.init(
        RedisBackend(redis_client),
        prefix='fastapi-cache',
    )
    if settings.RUN_PARSER_ON_STARTUP:
        asyncio.create_task(check_last_date_parser_spmx())

    yield
    await disconnect_redis(redis_client)


app = FastAPI(
    title=settings.APP_TITLE, description=settings.APP_DESCRIPTION, debug=True, lifespan=lifespan
)
app.middleware('http')(LoggingMiddleware())

app.include_router(main_router)
