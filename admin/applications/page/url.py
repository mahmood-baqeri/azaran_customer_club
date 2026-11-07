from django.urls import path
from applications.page.views import admin, content_item

app_name = "pagemanagement"

urlpatterns = [
    # admin/web urls
    path('', admin.page_list, name='admin_page_list'),
    path('add/', admin.page_add, name='admin_page_add'),
    path('edit/<int:pk>/', admin.page_edit, name='admin_page_edit'),
    path('delete/', admin.page_delete, name='admin_page_delete'),
    path('toggle-status/', admin.page_toggle_status, name='admin_page_toggle_status'),
    path('bulk-action/', admin.page_bulk_action, name='admin_page_bulk_action'),
    path('stats/', admin.page_stats, name='admin_page_stats'),

    # gallery
    path('upload-gallery/', admin.upload_gallery_images, name='upload_gallery'),
    path('delete-gallery-image/', admin.delete_gallery_image, name='delete_gallery_image'),
    path('update-gallery-order/', admin.update_gallery_order, name='update_gallery_order'),

    # content items
    path('content/<int:page_id>/content/', content_item.page_content_items, name='page_content_items'),
    path('api/content-item/create/<int:page_id>/', content_item.content_item_create, name='content_item_create'),
    path('api/content-item/edit/<int:item_id>/', content_item.content_item_edit, name='content_item_edit'),
    path('api/content-item/delete/<int:item_id>/', content_item.content_item_delete, name='content_item_delete'),
    path('api/content-item/reorder/', content_item.content_item_reorder, name='content_item_reorder'),
    path('api/content-item/<int:item_id>/data/', content_item.get_content_item_data, name='get_content_item_data'),
]