from .helper import normalize_files


def make_image_item(
    *,
    label='', 
    title='انتخاب تصویر', 
    name='image',
    input_id=None,
    existing=None,
    multiple=False,
    required=False,
    accept='image/*',
    allow_delete=False,
    remove_route=None,
    parent_id=None, 
    col_class='col-md-12',
):
    return {
        'b':           'imageUpload.html',
        'c':           col_class,
        'l':           label,
        'title':       title,
        'n':           name,
        'id':          input_id or f'id_{name}',
        'existing':    normalize_files(existing),
        'm':           1 if multiple else 0,
        'r':           1 if required else 0,
        'accept':      accept or 'image/*',
        'allowDelete': 1 if (allow_delete and remove_route) else 0,
        'removeRoute': remove_route or '',
        'parentId':    parent_id or '',
    }
    
    
    
    
    
    
#     الف) تصویر تک — ایجاد
# python
# make_image_item(
#     label='تصویر شاخص',
#     name='cover',
#     col_class='col-md-6',
# )
# ب) تصویر تک — ویرایش با تصویر موجود و حذف
# python
# make_image_item(
#     label='تصویر شاخص',
#     name='cover',
#     existing=[product.cover] if product.cover else [],
#     allow_delete=True,
#     remove_route=reverse('app_product:delete_cover', args=[product.pk]),
#     col_class='col-md-6',
# )
# ج) گالری چندتایی — با حذف تک‌تک
# python
# make_image_item(
#     label='گالری محصول',
#     name='gallery',
#     multiple=True,
#     existing=[g.image for g in product.gallery.all()],
#     allow_delete=True,
#     remove_route=reverse('app_product:remove_gallery_image', args=[product.pk]),
#     col_class='col-md-12',
# )
# د) دو کامپوننت در یک فرم (id یکتا)
# python
# items = [
#     make_image_item(
#         label='تصویر اصلی',
#         name='main_image',
#         input_id='id_main_image',
#         existing=[product.main_image] if product.main_image else [],
#         allow_delete=True,
#         remove_route=reverse('app_product:delete_main', args=[product.pk]),
#         col_class='col-md-6',
#     ),
#     make_image_item(
#         label='گالری',
#         name='gallery',
#         input_id='id_gallery',
#         multiple=True,
#         existing=[g.image for g in product.gallery.all()],
#         allow_delete=True,
#         remove_route=reverse('app_product:remove_gallery_image', args=[product.pk]),
#         col_class='col-md-6',
#     ),
# ]
# ۴) Backend نمونه — endpoint حذف
# python
# # applications/product/views/drf.py
# from rest_framework import viewsets, status
# from rest_framework.decorators import action
# from rest_framework.response import Response


# class ProductViewSet(viewsets.ModelViewSet):

#     @action(detail=True, methods=['post'], url_path='delete-main')
#     def delete_main(self, request, pk=None):
#         product = self.get_object()
#         if product.main_image:
#             product.main_image.delete(save=False)
#             product.main_image = None
#             product.save(update_fields=['main_image'])
#         return Response({'data': 'ok'})

#     @action(detail=True, methods=['post'], url_path='remove-gallery-image')
#     def remove_gallery_image(self, request, pk=None):
#         product = self.get_object()
#         image_id = request.data.get('imageId')
#         index    = request.data.get('index')

#         qs = product.gallery.all()
#         if image_id not in (None, '', 'null'):
#             obj = qs.filter(pk=image_id).first()
#         else:
#             try:
#                 index = int(index)
#                 obj = list(qs.order_by('id'))[index]
#             except (TypeError, ValueError, IndexError):
#                 obj = None

#         if not obj:
#             return Response({'data': 'تصویر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)

#         obj.image.delete(save=False)
#         obj.delete()
#         return Response({'data': 'ok'})