# Path: applications/factor/views/__init__.py

# applications/factor/views/__init__.py

from .factor_view import (
    factor_approve_action,
    factor_create,
    factor_delete,
    factor_detail,
    factor_export,
    factor_index,
    factor_reject_action,
    factor_update,
)

__all__ = [
    "factor_index", "factor_export",
    "factor_create", "factor_update", "factor_detail", "factor_delete",
    "factor_approve_action", "factor_reject_action",
]