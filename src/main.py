from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from api.v1.routers import main_router
from core.config import settings
from core.redis_utils import connect_redis, disconect_redis
from core.logger import LoggingMiddleware, logger
# from services.check_data_parser import check_last_date_parser_spmx
# from core.db_depends import AsyncSessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = await connect_redis()
    FastAPICache.init(RedisBackend(redis_client), prefix='fastapi-cache')
    yield
    await disconect_redis(redis_client)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     redis_client = await init_redis()
#     FastAPICache.init(RedisBackend(redis_client), prefix='fastapi-cache')
#     # async with AsyncSessionLocal() as session:
#     #     await check_last_date_parser_spmx(session)
#     yield
#     # await close_redis()
#     await redis_client.close()
#     logger.info('Отключено от Redis.')

app = FastAPI(
    title=settings.APP_TITLE, description=settings.APP_DESCRIPTION, debug=True, lifespan=lifespan
)
app.middleware('http')(LoggingMiddleware())

app.include_router(main_router)
