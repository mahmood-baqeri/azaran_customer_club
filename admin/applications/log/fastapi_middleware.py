"""
Middleware لاگ برای FastAPI.
از همان مدل RequestLog جنگو استفاده می‌کند.
"""

import time
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from .parsers import parse_user_agent, mask_sensitive, get_client_ip


logger = logging.getLogger(__name__)


class FastAPIRequestLogMiddleware(BaseHTTPMiddleware):
    EXCLUDED = ("/docs", "/redoc", "/openapi.json", "/health")

    async def dispatch(self, request: Request, call_next):
        if any(request.url.path.startswith(p) for p in self.EXCLUDED):
            return await call_next(request)

        start = time.monotonic()
        error_message = None
        status_code = None
        response = None

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            error_message = str(e)
            status_code = 500
            raise
        finally:
            duration_ms = int((time.monotonic() - start) * 1000)
            ua = request.headers.get("user-agent", "") or ""
            ua_info = parse_user_agent(ua)

            # query
            query_params = {
                k: mask_sensitive(k, v) for k, v in request.query_params.items()
            }

            # body
            body_params = {}
            if request.method in ("POST", "PUT", "PATCH"):
                try:
                    raw = await request.json()
                    if isinstance(raw, dict):
                        body_params = {
                            k: mask_sensitive(k, v) for k, v in raw.items()
                        }
                except Exception:
                    pass

            try:
                from applications.log.models import RequestLog
                await RequestLog.objects.acreate(
                    user=None,
                    is_authenticated=False,
                    method=request.method,
                    path=request.url.path,
                    full_path=str(request.url),
                    view_name=None,
                    module="fastapi",
                    query_params=query_params,
                    body_params=body_params,
                    status_code=status_code,
                    is_ajax=False,
                    is_api=True,
                    success=error_message is None and (
                        status_code is None or status_code < 400
                    ),
                    error_message=error_message,
                    action=request.headers.get("x-action"),
                    duration_ms=duration_ms,
                    ip=get_client_ip(request),
                    user_agent=ua[:2000] if ua else None,
                    os=ua_info.get("os"),
                    device=ua_info.get("device"),
                    browser=ua_info.get("browser"),
                    referer=request.headers.get("referer"),
                )
            except Exception as e:
                logger.exception("FastAPI request log failed: %s", e)

        return response