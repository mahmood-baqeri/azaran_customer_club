# Path: applications/support/views/__init__.py

# applications/support/views/__init__.py

from .support_view import (
    support_change_status,
    support_close,
    support_create,
    support_delete,
    support_detail,
    support_export,
    support_index,
    support_send_message,
    support_update,
)

__all__ = [
    "support_index", "support_export",
    "support_create", "support_update", "support_detail", "support_delete",
    "support_change_status", "support_close", "support_send_message",
]