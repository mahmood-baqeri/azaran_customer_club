# Path: applications/core/forms/fileUpload_item.py

from .helper import normalize_files


def make_file_item(
    *, 
    label='', 
    name='file', 
    input_id=None,
    files=None, 
    multiple=False, 
    required=False,
    accept=None, 
    allow_delete=False, 
    remove_route=None,
    col_class='col-md-12',
):
    return {
        'b':           'fileUpload.html',
        'l':           label,
        'c':           col_class,
        'n':           name,
        'id':          input_id or f'id_{name}',
        'files':       normalize_files(files),
        'm':           1 if multiple else 0,
        'r':           1 if required else 0,
        'accept':      accept or '',
        'allowDelete': 1 if (allow_delete and remove_route) else 0,
        'removeRoute': remove_route or '',
    }
    



# الف) فایل تک — ایجاد (بدون مقدار اولیه)
# python
# from applications.core.utils.forms import make_file_item

# def create_document(request):
#     data = {
#         'pageTitle': 'ثبت سند',
#         'storeUrl':  reverse('app_doc:create'),
#         'items': [
#             make_file_item(
#                 label='فایل سند',
#                 name='document',
#                 accept='application/pdf, image/*',
#                 required=True,
#             ),
#         ],
#     }
#     return render(request, 'layout/form.html', {'data': data})
# ب) فایل تک — ویرایش (با فایل موجود + اجازه‌ی حذف)
# python
# def edit_document(request, pk):
#     doc = get_object_or_404(Document, pk=pk)

#     data = {
#         'pageTitle': 'ویرایش سند',
#         'storeUrl':  reverse('app_doc:edit', args=[pk]),
#         'items': [
#             make_file_item(
#                 label='فایل سند',
#                 name='document',
#                 accept='application/pdf, image/*',
#                 files=[doc.file] if doc.file else [],   # FieldFile
#                 allow_delete=True,
#                 remove_route=reverse('app_doc:delete_file', args=[pk]),
#             ),
#         ],
#     }
#     return render(request, 'layout/form.html', {'data': data})
# ج) فایل چندتایی — گالری تصاویر
# python
# def edit_gallery(request, pk):
#     gallery = get_object_or_404(Gallery, pk=pk)
#     images  = [img.image for img in gallery.images.all()]   # لیست FieldFile

#     data = {
#         'pageTitle': 'ویرایش گالری',
#         'storeUrl':  reverse('app_gallery:edit', args=[pk]),
#         'items': [
#             make_file_item(
#                 label='تصاویر گالری',
#                 name='images',
#                 accept='image/*',
#                 multiple=True,
#                 files=images,
#                 allow_delete=True,
#                 remove_route=reverse('app_gallery:remove_image', args=[pk]),
#             ),
#         ],
#     }
#     return render(request, 'layout/form.html', {'data': data})
# د) چند فایل آپلود در یک فرم (نام و id یکتا)
# python
# items = [
#     make_file_item(
#         label='تصویر اصلی',
#         name='main_image',
#         input_id='id_main_image',
#         accept='image/*',
#         files=[product.main_image] if product.main_image else [],
#         allow_delete=True,
#         remove_route=reverse('app_product:delete_main_image', args=[product.pk]),
#         col_class='col-md-6',
#     ),
#     make_file_item(
#         label='گالری',
#         name='gallery',
#         input_id='id_gallery',
#         accept='image/*',
#         multiple=True,
#         files=[g.image for g in product.gallery.all()],
#         allow_delete=True,
#         remove_route=reverse('app_product:remove_gallery_image', args=[product.pk]),
#         col_class='col-md-6',
#     ),
# ]
# ۴) Backend حذف فایل — نمونه
# چون remove_route استاتیک است و شناسه‌ی فایل در payload می‌آید:

# python
# # applications/gallery/views/drf.py
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework import viewsets, status


# class GalleryViewSet(viewsets.ModelViewSet):
#     # ...

#     @action(detail=True, methods=['post'], url_path='remove-image')
#     def remove_image(self, request, pk=None):
#         gallery = self.get_object()

#         file_id = request.data.get('fileId')
#         index   = request.data.get('index')

#         qs = gallery.images.all()
#         if file_id not in (None, '', 'null'):
#             qs = qs.filter(pk=file_id)
#         else:
#             try:
#                 index = int(index)
#             except (TypeError, ValueError):
#                 return Response({'data': 'شناسه نامعتبر'}, status=400)
#             page = list(qs.order_by('id'))
#             if index >= len(page):
#                 return Response({'data': 'فایل یافت نشد'}, status=404)
#             qs = type(qs).objects.filter(pk=page[index].pk)

#         deleted, _ = qs.delete()
#         if deleted:
#             return Response({'data': 'ok'})
#         return Response({'data': 'فایل یافت نشد'}, status=404)
