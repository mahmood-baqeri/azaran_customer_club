# applications/user/view/__init__.py
# نقطه‌ی ورود — همه‌ی ویوها از user_view.py export می‌شوند

from .user_view import (
    user_index,
    user_create,
    user_update,
    user_delete,
    user_detail,
    user_verify_mobile_action,
    user_toggle_active_action,
    user_certificate_approve,
    user_certificate_reject,
)

__all__ = [
    "user_index",
    "user_create",
    "user_update",
    "user_delete",
    "user_detail",
    "user_verify_mobile_action",
    "user_toggle_active_action",
    "user_certificate_approve",
    "user_certificate_reject",
]