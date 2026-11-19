# Path: applications/faq/views/__init__.py

# applications/faq/views/__init__.py

from .faq_category import (
    category_create,
    category_delete,
    category_export,
    category_index,
    category_toggle_active,
    category_update,
)
from .faq import (
    answer_create,
    answer_delete,
    answer_toggle_active,
    faq_delete,
    faq_detail,
    faq_export,
    faq_index,
    faq_toggle_active,
)

__all__ = [
    # Category
    "category_index", "category_export",
    "category_create", "category_update", "category_delete",
    "category_toggle_active",
    # FAQ
    "faq_index", "faq_export", "faq_detail", "faq_delete", "faq_toggle_active",
    # Answer
    "answer_create", "answer_toggle_active", "answer_delete",
]