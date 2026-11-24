import redis.asyncio as redis

from src.core.config import get_settings

# 创建 redis Client
settings = get_settings()
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
    encoding="utf-8",
)

# 模块级别创建 Redis 客户端实例（复用链接池）
_redis_client = redis.Redis(connection_pool=redis_pool)


async def get_redis() -> redis.Redis:
    return _redis_client
