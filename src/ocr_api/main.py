from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from ocr_api.routes import api_router
from ocr_api.utils.errors import register_error_handlers
from dotenv import load_dotenv
import redis.asyncio as aioredis
import os
import logging
from ocr_api.dependencies import limiter

info_logger = logging.getLogger("info_logger")

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    REDIS_URL = os.getenv("REDIS_URL")

    app.state.redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    info_logger.info("Successfully connected to Redis")

    limiter._storage_uri = REDIS_URL
    app.state.limiter = limiter

    yield

    await app.state.redis.close()
    info_logger.info("Redis disconnected")


app = FastAPI(title="OCR API", lifespan=lifespan)

register_error_handlers(app)


app.include_router(api_router)
