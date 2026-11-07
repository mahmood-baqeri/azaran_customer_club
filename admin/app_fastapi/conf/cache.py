import time
from typing import Any, Dict, Optional
from fastapi import Depends


# یک کش ساده در حافظه (RAM)
class SimpleAsyncCache:
    def __init__(self):
        # ذخیره داده‌ها به شکل { key: (value, expire_timestamp) }
        self._store: Dict[str, tuple[Any, Optional[float]]] = {}

    async def set(self, key: str, value: Any, expire: Optional[int] = None):
        """
        ذخیره مقدار با کلید مشخص و زمان انقضا (expire بر حسب ثانیه)
        """
        expire_time = time.time() + expire if expire else None
        self._store[key] = (value, expire_time)

    async def get(self, key: str) -> Optional[Any]:
        """
        دریافت مقدار از کش (اگر منقضی نشده باشد)
        """
        data = self._store.get(key)
        if not data:
            return None
        value, expire_time = data
        if expire_time and time.time() > expire_time:
            await self.delete(key)
            return None
        return value

    async def delete(self, key: str):
        """
        حذف کلید از کش
        """
        self._store.pop(key, None)

    async def clear(self):
        """
        پاک کردن کل کش
        """
        self._store.clear()


# ساخت یک نمونه‌ی سراسری (singleton)
cache_instance = SimpleAsyncCache()


# Dependency برای FastAPI
async def get_cache():
    """
    وابستگی FastAPI برای تزریق کش
    """
    return cache_instance
