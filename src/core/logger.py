import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True, parents=True)
LOG_FILE = LOG_DIR / 'app.log'

logger = logging.getLogger('parser')
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(funcName)s() - %(message)s'
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1000000, backupCount=3, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования всех HTTP-запросов"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response: Response = await call_next(request)
        duration = time.time() - start_time
        logger.info(
            f'Request: {request.method} {request.url} - {duration:.3f} sec; '
            f'Response: {response.status_code}'
        )
        return response
