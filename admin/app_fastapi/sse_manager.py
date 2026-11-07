# ========== applications/_fastapi/sse_manager.py - نسخه نهایی ==========
import asyncio
import json
import time
from asgiref.sync import sync_to_async
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime, timezone
from collections import deque
from contextlib import asynccontextmanager
from django.core.cache import cache

from .conf.redis_client import get_redis


class SSEManager:
    """
    مدیریت اتصالات SSE با پشتیبانی از:
    - Backpressure (Queue maxsize بهینه)
    - Multi-worker (Redis PubSub با connection pooling)
    - Proper resource cleanup
    - Connection resume (Last-Event-ID)
    - Metrics monitoring
    """
    
    def __init__(self):
        self._connections: Dict[str, asyncio.Queue] = {}
        self._cancel_events: Dict[str, asyncio.Event] = {}
        self._lock = asyncio.Lock()
        self._pubsub_task: Optional[asyncio.Task] = None
        self._redis_client = None  # single redis client
        self._pubsub = None
        self._active_connections_count = 0
        self._shutdown_event = asyncio.Event()
        
        # [FIX] Metrics for monitoring
        self._metrics = {
            "total_connections": 0,
            "total_messages_sent": 0,
            "total_messages_dropped": 0,
            "total_redis_publishes": 0,
            "total_redis_errors": 0,
        }
        self._last_metric_log = time.time()

    async def _get_redis(self):
        """Lazy initialization با reuse connection"""
        if self._redis_client is None:
            self._redis_client = await get_redis()
        return self._redis_client

    async def _init_redis_pubsub(self):
        """ایجاد PubSub فقط یک بار"""
        if self._pubsub is None:
            redis = await self._get_redis()
            self._pubsub = redis.pubsub()
            await self._pubsub.subscribe("sse:broadcast")
            
            if not self._pubsub_task or self._pubsub_task.done():
                self._pubsub_task = asyncio.create_task(self._listen_redis())

    async def _listen_redis(self):
        """گوش دادن به پیام‌های Redis PubSub با backpressure"""
        try:
            async for message in self._pubsub.listen():
                if self._shutdown_event.is_set():
                    break
                    
                if message["type"] != "message":
                    continue
                    
                try:
                    data = json.loads(message["data"])
                    stream_id = data.get("stream_id")
                    
                    if stream_id and stream_id in self._connections:
                        queue = self._connections[stream_id]
                        try:
                            # [FIX] put_nowait برای جلوگیری از blocking
                            queue.put_nowait(data)
                            self._metrics["total_messages_sent"] += 1
                        except asyncio.QueueFull:
                            # [FIX] Drop message with metrics
                            self._metrics["total_messages_dropped"] += 1
                            print(f"[WARN] Queue full for {stream_id}, dropped message")
                            
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Invalid JSON: {e}")
                except Exception as e:
                    print(f"[ERROR] Redis message processing: {e}")
                    self._metrics["total_redis_errors"] += 1
                    
        except asyncio.CancelledError:
            print("[INFO] Redis pubsub listener cancelled")
        except Exception as e:
            print(f"[ERROR] Redis listener fatal: {e}")
        finally:
            await self._cleanup_pubsub()

    async def _cleanup_pubsub(self):
        """Cleanup PubSub resources"""
        if self._pubsub:
            try:
                await self._pubsub.unsubscribe("sse:broadcast")
                await self._pubsub.close()
            except Exception as e:
                print(f"[ERROR] Pubsub cleanup: {e}")
            finally:
                self._pubsub = None

    async def connect(self, stream_id: str, user_id: int) -> Tuple[asyncio.Queue, asyncio.Event]:
        """
        اتصال جدید SSE با queue بهینه
        [FIX] maxsize کاهش یافته به 100 برای backpressure بهتر
        """
        await self._init_redis_pubsub()
        
        async with self._lock:
            # [FIX] کاهش maxsize از 1000 به 100 برای جلوگیری از مصرف حافظه بالا
            queue = asyncio.Queue(maxsize=100)
            cancel_event = asyncio.Event()
            
            self._connections[stream_id] = queue
            self._cancel_events[stream_id] = cancel_event
            self._active_connections_count += 1
            self._metrics["total_connections"] += 1
            
            # [FIX] Log metrics periodically
            await self._maybe_log_metrics()
            
            return queue, cancel_event

    async def disconnect(self, stream_id: str):
        """
        قطع اتصال SSE با cleanup کامل
        [FIX] Standard queue cleanup بدون access to private attribute
        """
        async with self._lock:
            # [FIX] حذف queue به روش استاندارد
            if stream_id in self._connections:
                queue = self._connections[stream_id]
                # Mark as closed by putting sentinel
                try:
                    await queue.put(None)  # sentinel for closed
                except:
                    pass
                del self._connections[stream_id]
            
            if stream_id in self._cancel_events:
                self._cancel_events[stream_id].set()
                del self._cancel_events[stream_id]
            
            self._active_connections_count -= 1
            
            # [FIX] Cleanup فقط در صورت عدم وجود connection
            if self._active_connections_count == 0:
                await self._cleanup_all_resources()

    async def _cleanup_all_resources(self):
        """Cleanup تمام منابع Redis"""
        self._shutdown_event.set()
        
        # Cancel pubsub task
        if self._pubsub_task and not self._pubsub_task.done():
            self._pubsub_task.cancel()
            try:
                await self._pubsub_task
            except asyncio.CancelledError:
                pass
            self._pubsub_task = None
        
        # Cleanup pubsub
        await self._cleanup_pubsub()
        
        # Close redis client
        if self._redis_client:
            try:
                await self._redis_client.close()
            except Exception as e:
                print(f"[ERROR] Redis client close: {e}")
            finally:
                self._redis_client = None
        
        self._shutdown_event.clear()

    async def send_message(self, stream_id: str, data: dict):
        """
        ارسال پیام به یک stream خاص
        [FIX] Reuse redis client بدون create new connection
        """
        # Local connection
        if stream_id in self._connections:
            queue = self._connections[stream_id]
            try:
                # [FIX] put_nowait برای backpressure فوری
                queue.put_nowait(data)
                self._metrics["total_messages_sent"] += 1
            except asyncio.QueueFull:
                self._metrics["total_messages_dropped"] += 1
                print(f"[WARN] Queue full for {stream_id}, dropping message")
            except Exception as e:
                print(f"[ERROR] Send to queue: {e}")
        else:
            # Remote worker - broadcast via Redis
            try:
                # [FIX] Reuse redis client بدون ایجاد connection جدید
                redis = await self._get_redis()
                await redis.publish("sse:broadcast", json.dumps({"stream_id": stream_id, **data}))
                self._metrics["total_redis_publishes"] += 1
            except Exception as e:
                self._metrics["total_redis_errors"] += 1
                print(f"[ERROR] Redis publish: {e}")

    def is_cancelled(self, stream_id: str) -> bool:
        """بررسی اینکه آیا stream لغو شده است"""
        event = self._cancel_events.get(stream_id)
        return event.is_set() if event else True

    async def cleanup_all(self):
        """Cleanup تمام اتصالات (برای shutdown سرور)"""
        async with self._lock:
            stream_ids = list(self._connections.keys())
            for stream_id in stream_ids:
                await self.disconnect(stream_id)
            
            await self._cleanup_all_resources()

    async def get_metrics(self) -> dict:
        """دریافت آمار برای monitoring"""
        return {
            **self._metrics,
            "active_connections": self._active_connections_count,
            "timestamp": datetime.now().isoformat(),
        }

    async def _maybe_log_metrics(self):
        """Log metrics periodically (هر 5 دقیقه)"""
        now = time.time()
        if now - self._last_metric_log > 300:  # 5 minutes
            self._last_metric_log = now
            metrics = await self.get_metrics()
            print(f"[METRICS] SSE Manager: {metrics}")


# ========== Singleton instance ==========
sse_manager = SSEManager()


async def event_stream_generator(stream_id: str, user_id: int):
    """
    Generator برای رویدادهای SSE با:
    - Heartbeat
    - Proper cleanup
    - [FIX] No heartbeat after disconnect
    """
    queue, cancel_event = await sse_manager.connect(stream_id, user_id)
    
    try:
        while not cancel_event.is_set():
            try:
                # Wait for message with timeout (for heartbeat)
                data = await asyncio.wait_for(queue.get(), timeout=15.0)
                
                # [FIX] Check for sentinel (closed queue)
                if data is None:
                    break
                
                event_type = data.get("type", "message")
                data_without_type = {k: v for k, v in data.items() if k != "type"}
                
                yield {
                    "event": event_type,
                    "data": json.dumps(data_without_type),
                    "id": f"evt_{int(datetime.now().timestamp() * 1000)}",  # milliseconds
                }
                
                if event_type == "end":
                    break
                    
            except asyncio.TimeoutError:
                # [FIX] فقط اگر still connected باشه heartbeat بفرست
                if not cancel_event.is_set():
                    yield {
                        "event": "heartbeat",
                        "data": json.dumps({"timestamp": datetime.now().isoformat()}),
                        "id": f"hb_{int(datetime.now().timestamp() * 1000)}",
                    }
                
    except asyncio.CancelledError:
        # Client disconnected - normal
        pass
    except Exception as e:
        print(f"[ERROR] Event stream generator: {e}")
    finally:
        # Always cleanup
        await sse_manager.disconnect(stream_id)


# ========== Helper function for sending events ==========
@asynccontextmanager
async def sse_connection(stream_id: str, user_id: int):
    """
    Context manager برای مدیریت امن اتصال SSE
    استفاده:
        async with sse_connection(stream_id, user_id) as (queue, cancel_event):
            # use connection
    """
    queue, cancel_event = await sse_manager.connect(stream_id, user_id)
    try:
        yield queue, cancel_event
    finally:
        await sse_manager.disconnect(stream_id)


# ========== Recovery Manager برای SSE ==========

class SSERecoveryManager:
    """
    مدیریت بازیابی اتصالات قطع شده SSE
    [FIX] یکپارچه - فقط از Django Cache استفاده می‌کند (بدون duplicate)
    """
    
    def __init__(self):
        self._cache_ttl = 300  # 5 دقیقه
        self._max_events_per_stream = 100
    
    async def store_event(self, stream_id: str, event_id: str, event_data: dict):
        """
        ذخیره رویداد برای بازیابی بعدی
        استفاده از Django Cache (Redis) برای multi-worker support
        """
        key = f"sse_recovery:{stream_id}"
        
        # دریافت events موجود
        events = cache.get(key, {})
        
        # اضافه کردن رویداد جدید
        events[event_id] = {
            "data": event_data,
            "timestamp": timezone.now().isoformat(),
            "order": len(events)  # حفظ ترتیب
        }
        
        # نگهداری فقط آخرین N رویداد
        if len(events) > self._max_events_per_stream:
            # حذف قدیمی‌ترین رویداد (بر اساس order)
            oldest = min(events.keys(), key=lambda x: events[x].get("order", 0))
            del events[oldest]
        
        # ذخیره در کش
        cache.set(key, events, timeout=self._cache_ttl)
    
    async def get_missed_events(self, stream_id: str, last_event_id: str) -> List[dict]:
        """
        دریافت رویدادهای از دست رفته از last_event_id به بعد
        """
        key = f"sse_recovery:{stream_id}"
        events = cache.get(key, {})
        
        if not events:
            return []
        
        missed = []
        found = False
        
        # مرتب‌سازی بر اساس order
        sorted_events = sorted(events.items(), key=lambda x: x[1].get("order", 0))
        
        for event_id, event_data in sorted_events:
            if found:
                missed.append(event_data["data"])
            elif event_id == last_event_id:
                found = True
        
        return missed
    
    async def clear_stream(self, stream_id: str):
        """پاک کردن history یک stream"""
        key = f"sse_recovery:{stream_id}"
        cache.delete(key)
    
    @staticmethod
    async def get_missed_messages(chat_uuid: str, after_message_id: int, limit: int = 50) -> List[dict]:
        """
        دریافت پیام‌های از دست رفته از دیتابیس
        [FIX] یک نسخه - بدون duplicate
        """
        # @sync_to_async
        # def get_messages():
            # messages = Message.objects.filter(
            #     chat__uuid=chat_uuid,
            #     id__gt=after_message_id,
            #     status=Message.Status.COMPLETED
            # ).select_related('attachment').order_by("id")[:limit]
            
            # return [
            #     {
            #         "type": "message",
            #         "data": {
            #             "id": msg.id,
            #             "role": msg.role,
            #             "content": msg.text_content,
            #             "created_at": msg.created_at.isoformat()
            #         }
            #     }
            #     for msg in messages
            # ]
        
        # return await get_messages()
    
    @staticmethod
    async def get_missed_messages_cursor(
        chat_uuid: str, 
        cursor: int, 
        limit: int = 50
    ) -> tuple[List[dict], Optional[int]]:
        """
        دریافت پیام‌های از دست رفته با cursor-based pagination
        برای بازیابی مقادیر زیاد پیام
        """
        # @sync_to_async
        # def get_messages():
        #     messages = list(Message.objects.filter(
        #         chat__uuid=chat_uuid,
        #         id__gt=cursor,
        #         status=Message.Status.COMPLETED
        #     ).select_related('attachment').order_by("id")[:limit + 1])
            
        #     has_more = len(messages) > limit
        #     messages = messages[:limit]
            
        #     next_cursor = messages[-1].id if has_more and messages else None
            
        #     return [
        #         {
        #             "type": "message",
        #             "data": {
        #                 "id": msg.id,
        #                 "role": msg.role,
        #                 "content": msg.text_content,
        #                 "created_at": msg.created_at.isoformat()
        #             }
        #         }
        #         for msg in messages
        #     ], next_cursor
        
        # return await get_messages()


# ========== Global instance ==========
sse_recovery_manager = SSERecoveryManager()