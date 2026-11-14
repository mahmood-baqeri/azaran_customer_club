# applications/gift/views/__init__.py

from .gift import (
    delete_gallery_photo,
    gift_create,
    gift_delete,
    gift_index,
    gift_update,
)
from .order import (
    order_assign,
    order_detail,
    order_index,
    order_note,
    order_update_status,
)

__all__ = [
    # gift
    "gift_index",
    "gift_create",
    "gift_update",
    "gift_delete",
    "delete_gallery_photo",
    # order
    "order_index",
    "order_detail",
    "order_update_status",
    "order_assign",
    "order_note",
]