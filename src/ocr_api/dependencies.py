import redis.asyncio as aioredis
from fastapi import Request

"""
Functions used for dependency injection in routers
"""


async def get_redis(request: Request) -> aioredis.Redis:
    return request.app.state.redis
