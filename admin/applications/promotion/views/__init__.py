# applications/promotion/views/__init__.py

from .promotion import (
    promotion_create,
    promotion_delete,
    promotion_detail,
    promotion_index,
    promotion_item_create,
    promotion_item_delete,
    promotion_item_update,
    promotion_update,
)
from .promotion_order import (
    order_assign,
    order_detail,
    order_index,
    order_update_status,
)

__all__ = [
    # promotion
    "promotion_index",
    "promotion_create",
    "promotion_update",
    "promotion_delete",
    "promotion_detail",
    "promotion_item_create",
    "promotion_item_update",
    "promotion_item_delete",
    # order
    "order_index",
    "order_detail",
    "order_update_status",
    "order_assign",
]