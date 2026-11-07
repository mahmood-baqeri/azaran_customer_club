import redis.asyncio as redis
from typing import Optional
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# ========== خواندن تنظیمات از settings.py ==========
def get_redis_settings():
    """
    دریافت تنظیمات Redis از فایل settings.py
    با پشتیبانی از متغیرهای محیطی
    """
    # خواندن از settings یا استفاده از مقادیر پیش‌فرض
    redis_host = getattr(settings, 'REDIS_HOST', '127.0.0.1')
    redis_port = getattr(settings, 'REDIS_PORT', 6379)
    redis_password = getattr(settings, 'REDIS_PASS', '')
    redis_db = getattr(settings, 'REDIS_DB', 0)
    redis_cache_db = getattr(settings, 'REDIS_CACHE_DB', 1)
    
    # ساخت URL با رمز عبور (اگر تنظیم شده باشد)
    if redis_password:
        redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
    else:
        redis_url = f"redis://{redis_host}:{redis_port}/{redis_db}"
    
    return {
        'host': redis_host,
        'port': redis_port,
        'password': redis_password,
        'db': redis_db,
        'cache_db': redis_cache_db,
        'url': redis_url,
    }


# دریافت تنظیمات
REDIS_CONFIG = get_redis_settings()
REDIS_URL = REDIS_CONFIG['url']


class RedisClient:
    """
    کلاینت Redis با پشتیبانی از:
    - خواندن تنظیمات از settings.py
    - Connection Pool
    - Retry on timeout
    - Health check
    """
    _client: Optional[redis.Redis] = None
    _pubsub: Optional[redis.client.PubSub] = None
    
    @classmethod
    async def get_client(cls) -> redis.Redis:
        """دریافت کلاینت Redis با تنظیمات از settings.py"""
        if cls._client is None:
            try:
                # استفاده از URL ساخته شده از تنظیمات
                cls._client = redis.from_url(
                    REDIS_URL,
                    decode_responses=True,
                    max_connections=getattr(settings, 'REDIS_MAX_CONNECTIONS', 20),
                    socket_connect_timeout=getattr(settings, 'REDIS_SOCKET_TIMEOUT', 5),
                    socket_timeout=getattr(settings, 'REDIS_SOCKET_TIMEOUT', 5),
                    retry_on_timeout=getattr(settings, 'REDIS_RETRY_ON_TIMEOUT', True),
                    health_check_interval=getattr(settings, 'REDIS_HEALTH_CHECK_INTERVAL', 30),
                )
                
                # تست اتصال
                await cls._client.ping()
                logger.info("✅ Redis connection established successfully")
                logger.info(f"   Host: {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
                logger.info(f"   DB: {REDIS_CONFIG['db']}")
                logger.info(f"   Password: {'Set' if REDIS_CONFIG['password'] else 'Not Set'}")
                
            except Exception as e:
                logger.error(f"❌ Redis connection failed: {e}")
                raise
        
        return cls._client
    
    @classmethod
    async def get_pubsub(cls) -> redis.client.PubSub:
        """دریافت PubSub client"""
        if cls._pubsub is None:
            client = await cls.get_client()
            cls._pubsub = client.pubsub()
        return cls._pubsub
    
    @classmethod
    async def close(cls):
        """بستن اتصالات Redis"""
        if cls._pubsub:
            try:
                await cls._pubsub.close()
                logger.info("✅ Redis PubSub closed")
            except Exception as e:
                logger.error(f"PubSub close error: {e}")
            finally:
                cls._pubsub = None
        
        if cls._client:
            try:
                await cls._client.close()
                logger.info("✅ Redis client closed")
            except Exception as e:
                logger.error(f"Redis client close error: {e}")
            finally:
                cls._client = None
    
    @classmethod
    async def flush_db(cls, db: Optional[int] = None):
        """پاک کردن دیتابیس (فقط برای توسعه)"""
        client = await cls.get_client()
        if db is not None:
            await client.select(db)
        await client.flushdb()
        logger.warning(f"⚠️ Redis DB {db or REDIS_CONFIG['db']} flushed")
    
    @classmethod
    async def get_info(cls) -> dict:
        """دریافت اطلاعات Redis"""
        client = await cls.get_client()
        info = await client.info()
        return {
            'redis_version': info.get('redis_version'),
            'uptime_seconds': info.get('uptime_in_seconds'),
            'connected_clients': info.get('connected_clients'),
            'used_memory_human': info.get('used_memory_human'),
            'total_commands_processed': info.get('total_commands_processed'),
            'role': info.get('role'),
        }


# ========== Helper Functions ==========
async def get_redis() -> redis.Redis:
    """ساده‌ترین راه برای دریافت کلاینت Redis"""
    return await RedisClient.get_client()


async def set_cache(key: str, value: str, ttl: int = 3600) -> bool:
    """ذخیره در کش با TTL"""
    try:
        client = await get_redis()
        await client.setex(key, ttl, value)
        return True
    except Exception as e:
        logger.error(f"Cache set error: {e}")
        return False


async def get_cache(key: str) -> Optional[str]:
    """دریافت از کش"""
    try:
        client = await get_redis()
        return await client.get(key)
    except Exception as e:
        logger.error(f"Cache get error: {e}")
        return None


async def delete_cache(key: str) -> bool:
    """حذف از کش"""
    try:
        client = await get_redis()
        await client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Cache delete error: {e}")
        return False


async def clear_cache(pattern: str = "*") -> int:
    """پاک کردن همه کلیدهای مطابق با الگو"""
    try:
        client = await get_redis()
        keys = await client.keys(pattern)
        if keys:
            return await client.delete(*keys)
        return 0
    except Exception as e:
        logger.error(f"Clear cache error: {e}")
        return 0


async def increment_counter(key: str, amount: int = 1) -> int:
    """افزایش شمارنده"""
    try:
        client = await get_redis()
        return await client.incrby(key, amount)
    except Exception as e:
        logger.error(f"Increment error: {e}")
        return 0


async def get_ttl(key: str) -> int:
    """دریافت زمان باقی‌مانده (ثانیه)"""
    try:
        client = await get_redis()
        return await client.ttl(key)
    except Exception as e:
        logger.error(f"TTL error: {e}")
        return -1