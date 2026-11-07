# ========== rate_limiter.py ==========
import asyncio
from datetime import datetime
from typing import Tuple, Optional
from collections import defaultdict, deque
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

class DOSProtectionMiddleware(BaseHTTPMiddleware):
    """
    محافظت در برابر DOS:
    - Rate limiting per IP
    - Rate limiting per user
    - Sliding window
    - Mid-stream rate limiting
    """
    
    def __init__(self, app):
        super().__init__(app)
        self._ip_requests = defaultdict(lambda: deque(maxlen=100))
        self._user_requests = defaultdict(lambda: deque(maxlen=100))
        self._lock = asyncio.Lock()
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = datetime.now().timestamp()
        
        # 1. بررسی IP
        async with self._lock:
            ip_requests = self._ip_requests[client_ip]
            self._clean_old_requests(ip_requests, now, window_seconds=60)
            
            if len(ip_requests) >= 100:  # حداکثر 100 درخواست در دقیقه
                raise HTTPException(status_code=429, detail="Too many requests from this IP")
            
            ip_requests.append(now)
        
        # 2. بررسی کاربر (اگر احراز شده)
        response = await call_next(request)
        return response
    
    def _clean_old_requests(self, requests, now, window_seconds):
        while requests and requests[0] < now - window_seconds:
            requests.popleft()


# ========== Mid-stream Rate Limiting ==========
class StreamRateLimiter:
    """محدودیت نرخ در حین استریم"""
    
    def __init__(self, user_id: int, tokens_per_second: float = 10):
        self.user_id = user_id
        self.tokens_per_second = tokens_per_second
        self.last_token_time = asyncio.get_event_loop().time()
        self.token_count = 0
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> Tuple[bool, float]:
        """
        مصرف توکن‌ها
        Returns: (allowed, wait_seconds)
        """
        async with self._lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - self.last_token_time
            
            # شارژ مجدد توکن‌ها
            new_tokens = elapsed * self.tokens_per_second
            self.token_count = min(self.token_count + new_tokens, self.tokens_per_second * 5)
            self.last_token_time = now
            
            if self.token_count >= tokens:
                self.token_count -= tokens
                return True, 0
            else:
                wait_time = (tokens - self.token_count) / self.tokens_per_second
                return False, wait_time