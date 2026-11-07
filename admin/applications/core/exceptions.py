# backend/apps/core/exceptions.py
from rest_framework.exceptions import APIException


class RateLimitExceeded(APIException):
    status_code = 429
    default_detail = 'تعداد درخواست‌های شما بیش از حد مجاز است'
    default_code = 'rate_limit_exceeded'


class SubscriptionExpired(APIException):
    status_code = 402
    default_detail = 'اشتراک شما منقضی شده است'
    default_code = 'subscription_expired'


class TokenLimitExceeded(APIException):
    status_code = 429
    default_detail = 'محدودیت توکن شما تمام شده است'
    default_code = 'token_limit_exceeded'