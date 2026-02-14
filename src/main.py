import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.v1.routers import main_router
from core.config import settings
from core.logger import LoggingMiddleware
from core.redis_utils import create_redis
from services.check_data_parser import check_last_date_parser_spmx


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await create_redis(settings=settings)
    app.state.redis = redis

    if settings.RUN_PARSER_ON_STARTUP:
        asyncio.create_task(check_last_date_parser_spmx())
    yield
    await redis.close()


app = FastAPI(
    title='SPIMEX Bulletin API',
    description='API для получения информации о итогах торгов '
    'Санкт-Петербургской международной товарно-сырьевой биржи (СПбМТСБ)',
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)

app.include_router(main_router)
