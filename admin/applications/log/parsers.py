"""
پارسرهای مشترک بین Django و FastAPI.
هیچ import وابسته به Django ندارد.
"""

import re

_SENSITIVE_KEYS = (
    "password", "passwd", "pass", "pwd",
    "token", "secret", "authorization", "api_key",
    "csrfmiddlewaretoken", "access", "refresh",
    "credit_card", "cvv", "otp", "code",
)

_BROWSER_PATTERNS = [
    (r"Edg/", "Edge"),
    (r"OPR/|Opera", "Opera"),
    (r"Chrome/(\d+)", "Chrome"),
    (r"Firefox/(\d+)", "Firefox"),
    (r"Safari/", "Safari"),
    (r"MSIE|Trident", "IE"),
    (r"curl/", "curl"),
    (r"PostmanRuntime/", "Postman"),
    (r"python-requests/", "python-requests"),
    (r"okhttp/", "OkHttp"),
]

_OS_PATTERNS = [
    (r"Windows NT 10", "Windows 10/11"),
    (r"Windows NT", "Windows"),
    (r"Mac OS X", "macOS"),
    (r"Android", "Android"),
    (r"iPhone|iPad|iPod", "iOS"),
    (r"Linux", "Linux"),
    (r"Ubuntu", "Ubuntu"),
]


def mask_sensitive(key, value):
    """مقدار فیلدهای حساس را با *** جایگزین می‌کند."""
    if not key:
        return value
    try:
        if any(s in str(key).lower() for s in _SENSITIVE_KEYS):
            return "***"
        if isinstance(value, list):
            return [mask_sensitive(key, v) for v in value]
        if isinstance(value, dict):
            return {k: mask_sensitive(k, v) for k, v in value.items()}
        return value
    except Exception:
        return "***"
 

def parse_user_agent(ua: str) -> dict:
    """استخراج مرورگر، سیستم‌عامل و نوع دستگاه از User-Agent."""
    result = {"browser": None, "os": None, "device": "Desktop"}
    if not ua:
        return result
    for pattern, name in _BROWSER_PATTERNS:
        if re.search(pattern, ua, re.IGNORECASE):
            result["browser"] = name
            break
    for pattern, name in _OS_PATTERNS:
        if re.search(pattern, ua, re.IGNORECASE):
            result["os"] = name
            break
    if re.search(r"Mobile|Android|iPhone|iPod|Windows Phone", ua, re.IGNORECASE):
        result["device"] = "Mobile"
    elif re.search(r"Tablet|iPad", ua, re.IGNORECASE):
        result["device"] = "Tablet"
    return result


# ============================================================
# get_client_ip — سازگار با Django و FastAPI
# ============================================================

def get_client_ip(request):
    """
    استخراج IP واقعی کاربر.

    - اگر request یک Django HttpRequest باشد: از META.
    - اگر request یک FastAPI/Starlette Request باشد: از headers و client.
    """
    # حالت Django
    try:
        meta = getattr(request, "META", None)
        if meta is not None:
            xff = meta.get("HTTP_X_FORWARDED_FOR")
            if xff:
                return xff.split(",")[0].strip()
            x_real = meta.get("HTTP_X_REAL_IP")
            if x_real:
                return x_real.strip()
            return meta.get("REMOTE_ADDR")
    except Exception:
        pass

    # حالت FastAPI / Starlette
    try:
        headers = getattr(request, "headers", None)
        if headers is not None:
            xff = headers.get("x-forwarded-for")
            if xff:
                return xff.split(",")[0].strip()
            x_real = headers.get("x-real-ip")
            if x_real:
                return x_real.strip()
        client = getattr(request, "client", None)
        if client is not None:
            host = getattr(client, "host", None)
            if host:
                return host
    except Exception:
        pass

    return None