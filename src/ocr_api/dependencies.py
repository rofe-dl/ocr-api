import redis.asyncio as aioredis
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

"""
Functions and vars used for dependency injection in routers
"""


async def get_redis(request: Request) -> aioredis.Redis:
    return request.app.state.redis


limiter = Limiter(key_func=get_remote_address)
