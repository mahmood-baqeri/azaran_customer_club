# Path: applications/user/view/__init__.py

# applications/user/views/__init__.py

from .user_view import (
    user_certificate_approve,
    user_certificate_reject,
    user_create,
    user_delete,
    user_detail,
    user_export,
    user_index,
    user_toggle_active_action,
    user_update,
    user_verify_mobile_action,
)
from .manager_view import (
    manager_change_password,       # ← جدید
    manager_create,
    manager_delete,
    manager_detail,
    manager_export,
    manager_index,
    manager_profile,               # ← جدید
    manager_toggle_active_action,
    manager_update,
)

__all__ = [
    # User
    "user_index", "user_export",
    "user_create", "user_update", "user_detail", "user_delete",
    "user_verify_mobile_action", "user_toggle_active_action",
    "user_certificate_approve", "user_certificate_reject",
    # Manager
    "manager_index", "manager_export",
    "manager_create", "manager_update", "manager_detail", "manager_delete",
    "manager_toggle_active_action",
    "manager_profile", "manager_change_password",   # ← جدید
]