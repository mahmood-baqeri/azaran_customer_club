# applications/gift/urls.py
from django.urls import path
from .views import gift

app_name = "app_gift"

urlpatterns = [
    # Gifts
    path("", gift.gift_index, name="gift_index"),
    path("create/", gift.gift_create, name="gift_create"),
    path("<int:id>/update/", gift.gift_update, name="gift_update"),
    path("<int:id>/delete/", gift.gift_delete, name="gift_delete"),
    
     # ✅ AJAX — حذف عکس گالری (طبق removeRoute در فرم)
    path("api/deletePhoto", gift.delete_gallery_photo, name="delete_photo"),
    
    # Orders
    path("orders/", gift.order_index, name="order_index"),
    path("orders/<int:id>/", gift.order_detail, name="order_detail"),
    path("orders/<int:id>/status/", gift.order_update_status, name="order_update_status"),
    path("orders/<int:id>/assign/", gift.order_assign, name="order_assign"),
    path("orders/<int:id>/note/", gift.order_note, name="order_note"),
]