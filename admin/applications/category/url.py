from django.urls import path
from applications.category.views import admin

app_name = "categorymanagement"

urlpatterns = [
    path('', admin.category_list, name='admin_category_list'),
    path('add/', admin.category_add, name='admin_category_add'),
    path('edit/<int:pk>/', admin.category_edit, name='admin_category_edit'),
    path('delete/', admin.category_delete, name='admin_category_delete'),
    path('toggle-status/', admin.category_toggle_status, name='admin_category_toggle_status'),
    path('bulk-action/', admin.category_bulk_action, name='admin_category_bulk_action'),
    path('<int:id>/children/', admin.category_children, name='admin_category_children'),
]