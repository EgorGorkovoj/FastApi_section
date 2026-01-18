from fastapi import APIRouter

from api.v1.endpoints import trading_router

main_router = APIRouter(prefix='/api/v1')

main_router.include_router(trading_router, tags=['Spimex Trading'])
