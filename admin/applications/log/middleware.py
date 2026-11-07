"""
Middleware لاگ درخواست‌ها

پشتیبانی از:
- کاربر لاگین‌شده با Session
- کاربر لاگین‌شده با JWT (SimpleJWT)
- کاربر لاگین‌شده با Token (DRF)
- کاربر مهمان
- درخواست‌های AJAX و API
- ذخیره‌ی غیرهمزمان برای جلوگیری از کندی request
"""

import json
import threading
import time
import logging

from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.urls import resolve, Resolver404
from django.http import QueryDict

from .models import RequestLog
from .parsers import mask_sensitive, parse_user_agent, get_client_ip


logger = logging.getLogger(__name__)


# ============================================================
# ذخیره‌ی غیرهمزمان
# ============================================================

def _save_log_async(log_data: dict):
    """ذخیره در thread جدا تا request کند نشه."""
    try:
        RequestLog.objects.create(**log_data)
    except Exception as e:
        logger.exception("RequestLog save failed: %s", e)


# ============================================================
# Middleware اصلی
# ============================================================

class RequestLogMiddleware(MiddlewareMixin):
    EXCLUDED_PATHS = (
        "/static/",
        "/media/",
        "/favicon.ico",
        "/health/",
        "/healthz/",
        "/metrics/",
        "/robots.txt",
        "/sitemap.xml",
        "/admin/jsi18n/",
        "/__debug__/",
        "/dump-die/",
    )

    EXCLUDED_EXTENSIONS = (
        ".css", ".js", ".map", ".png", ".jpg", ".jpeg",
        ".gif", ".svg", ".ico", ".woff", ".woff2", ".ttf",
        ".eot", ".mp4", ".webm", ".mp3", ".wav",
    )

    # ----------------------------------------------------------------
    def process_request(self, request):
        request._log_start_time = time.monotonic()
        return None

    def process_response(self, request, response):
        try:
            self._log(request, response)
        except Exception as e:
            logger.exception("RequestLog failed (response): %s", e)
        return response

    def process_exception(self, request, exception):
        try:
            self._log(request, response=None, error=exception)
        except Exception as e:
            logger.exception("RequestLog failed (exception): %s", e)
        return None

    # ----------------------------------------------------------------
    def _should_skip(self, request) -> bool:
        path = request.path_info or ""
        if any(path.startswith(p) for p in self.EXCLUDED_PATHS):
            return True
        if any(path.lower().endswith(ext) for ext in self.EXCLUDED_EXTENSIONS):
            return True
        return False

    def _resolve_view(self, request):
        try:
            match = resolve(request.path_info)
            view_name = match.view_name
            module = match.app_name or (
                view_name.split(":")[0] if view_name and ":" in view_name else None
            )
            return view_name, module
        except Resolver404:
            return None, None
        except Exception:
            return None, None

    def _extract_params(self, request):
        query_params = {}
        try:
            for key, values in request.GET.lists():
                query_params[key] = mask_sensitive(key, values)
        except Exception:
            pass

        body_params = {}
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = (request.content_type or "").lower()
            try:
                if "application/json" in content_type:
                    raw = request.body
                    if raw:
                        parsed = json.loads(raw.decode("utf-8"))
                        if isinstance(parsed, dict):
                            body_params = {
                                k: mask_sensitive(k, v) for k, v in parsed.items()
                            }
                        elif isinstance(parsed, list):
                            body_params = {
                                "_list": [mask_sensitive("item", x) for x in parsed[:20]]
                            }
                elif isinstance(request.POST, QueryDict):
                    for key in request.POST.keys():
                        body_params[key] = mask_sensitive(key, request.POST.getlist(key))
            except Exception:
                pass

        return query_params, body_params

    def _resolve_user(self, request):
        """
        1) request.user (Session/Middleware)
        2) JWTAuthentication
        3) TokenAuthentication
        4) SessionAuthentication
        """
        user = getattr(request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False):
            return user, True

        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header:
            for auth_class_path in (
                "rest_framework_simplejwt.authentication.JWTAuthentication",
                "rest_framework.authentication.TokenAuthentication",
                "rest_framework.authentication.SessionAuthentication",
            ):
                try:
                    module_path, class_name = auth_class_path.rsplit(".", 1)
                    module = __import__(module_path, fromlist=[class_name])
                    auth = getattr(module, class_name)()
                    result = auth.authenticate(request)
                    if result:
                        auth_user, _ = result
                        if auth_user and getattr(auth_user, "is_authenticated", False):
                            return auth_user, True
                except Exception:
                    continue

        return None, False

    def _get_action(self, request, view_name):
        action = getattr(request, "log_action", None)
        if action:
            return str(action)

        action = request.META.get("HTTP_X_ACTION")
        if action:
            return action

        if view_name:
            return view_name.split(":")[-1]

        return None

    def _log(self, request, response=None, error=None):
        if self._should_skip(request):
            return

        path = request.path_info or "/"
        view_name, module = self._resolve_view(request)
        query_params, body_params = self._extract_params(request)
        user, is_authenticated = self._resolve_user(request)

        ua = request.META.get("HTTP_USER_AGENT", "") or ""
        ua_info = parse_user_agent(ua)
        ip = get_client_ip(request)

        start = getattr(request, "_log_start_time", None)
        duration_ms = int((time.monotonic() - start) * 1000) if start else None

        status = getattr(response, "status_code", None)
        if status is None and error is not None:
            status = 500
        success = (error is None) and (status is None or status < 400)

        action = self._get_action(request, view_name)

        session_key = None
        try:
            session = getattr(request, "session", None)
            if session is not None:
                session_key = session.session_key
        except Exception:
            pass

        log_data = {
            "user": user if is_authenticated else None,
            "is_authenticated": is_authenticated,
            "method": (request.method or "GET").upper(),
            "path": path,
            "full_path": request.get_full_path() or path,
            "view_name": view_name,
            "module": module,
            "query_params": query_params,
            "body_params": body_params,
            "status_code": status,
            "is_ajax": request.headers.get("x-requested-with", "").lower() == "xmlhttprequest",
            "is_api": path.startswith("/api/") or "/api/" in path,
            "success": success,
            "error_message": (str(error) if error is not None else None),
            "action": action,
            "created": timezone.now(),
            "duration_ms": duration_ms,
            "ip": ip,
            "user_agent": ua[:2000] if ua else None,
            "os": ua_info.get("os"),
            "device": ua_info.get("device"),
            "browser": ua_info.get("browser"),
            "referer": request.META.get("HTTP_REFERER"),
            "session_key": session_key,
        }

        thread = threading.Thread(target=_save_log_async, args=(log_data,), daemon=True)
        thread.start()