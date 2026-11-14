# applications/gift/urls.py

from django.urls import path
from . import views

app_name = "app_gift"

urlpatterns = [
    # Gifts
    path("", views.gift_index, name="gift_index"),
    path("create/", views.gift_create, name="gift_create"),
    path("<int:id>/update/", views.gift_update, name="gift_update"),
    path("<int:id>/delete/", views.gift_delete, name="gift_delete"),

    # AJAX
    path("api/deletePhoto", views.delete_gallery_photo, name="delete_photo"),

    # Orders
    path("orders/", views.order_index, name="order_index"),
    path("orders/<int:id>/", views.order_detail, name="order_detail"),
    path("orders/<int:id>/status/", views.order_update_status, name="order_update_status"),
    path("orders/<int:id>/assign/", views.order_assign, name="order_assign"),
    path("orders/<int:id>/note/", views.order_note, name="order_note"),
]