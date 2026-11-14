# applications/promotion/urls.py

from django.urls import path
from . import views

app_name = "app_promotion"

urlpatterns = [
    # Promotion packs
    path("", views.promotion_index, name="promotion_index"),
    path("create/", views.promotion_create, name="promotion_create"),
    path("<int:id>/update/", views.promotion_update, name="promotion_update"),
    path("<int:id>/delete/", views.promotion_delete, name="promotion_delete"),
    path("<int:id>/", views.promotion_detail, name="promotion_detail"),

    # Promotion items (nested)
    path("<int:id>/item/create/", views.promotion_item_create, name="promotion_item_create"),
    path("<int:id>/item/<int:item_id>/update/", views.promotion_item_update, name="promotion_item_update"),
    path("<int:id>/item/<int:item_id>/delete/", views.promotion_item_delete, name="promotion_item_delete"),

    # Orders
    path("orders/", views.order_index, name="order_index"),
    path("orders/<int:id>/", views.order_detail, name="order_detail"),
    path("orders/<int:id>/status/", views.order_update_status, name="order_update_status"),
    path("orders/<int:id>/assign/", views.order_assign, name="order_assign"),
]