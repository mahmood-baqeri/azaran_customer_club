# Path: applications/core/views/drf.py

import os
from urllib.parse import unquote

from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from applications.core.serializers import TinyMCEUploadSerializer

UPLOAD_SUBDIR = 'tinymce_uploads'


class TinyMCEImageViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    lookup_value_regex = '[^/]+'   # اجازه می‌دهد نام فایل (با نقطه) به عنوان pk بیاید

    # GET  /v1/tinymce-image/  ← لیست تصاویر
    def list(self, request):
        media_path = os.path.join(settings.MEDIA_ROOT, UPLOAD_SUBDIR)
        if not os.path.exists(media_path):
            return Response({'images': []})

        images = [
            {
                'name': file_name,
                'url': request.build_absolute_uri(
                    f'{settings.MEDIA_URL}{UPLOAD_SUBDIR}/{file_name}'
                ),
            }
            for file_name in os.listdir(media_path)
        ]
        return Response({'images': images})

    # POST /v1/tinymce-image/  ← آپلود تصویر
    def create(self, request):
        serializer = TinyMCEUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data['file']

        os.makedirs(os.path.join(settings.MEDIA_ROOT, UPLOAD_SUBDIR), exist_ok=True)

        relative_path = os.path.join(UPLOAD_SUBDIR, uploaded_file.name)
        # در صورت وجود فایل هم‌نام، Django نام یکتا برمی‌گرداند
        saved_path = default_storage.save(relative_path, uploaded_file)

        file_url = request.build_absolute_uri(settings.MEDIA_URL + saved_path)
        return Response({'location': file_url}, status=status.HTTP_201_CREATED)

    # DELETE /v1/tinymce-image/<image_name>/  ← حذف تصویر
    def destroy(self, request, pk=None):
        image_name = unquote(pk)
        image_path = os.path.join(settings.MEDIA_ROOT, UPLOAD_SUBDIR, image_name)

        if os.path.exists(image_path):
            os.remove(image_path)
            return Response({'status': 'success', 'message': 'Image deleted successfully.'})

        return Response(
            {'status': 'error', 'message': 'Image not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )
        
    
    from rest_framework.decorators import action

    @action(detail=False, methods=['post'], url_path='delete')
    def destroy_by_name(self, request):
        image_name = request.data.get('image_name', '')
        image_path = os.path.join(settings.MEDIA_ROOT, UPLOAD_SUBDIR, image_name)
        if os.path.exists(image_path):
            os.remove(image_path)
            return Response({'status': 'success', 'message': 'Image deleted successfully.'})
        return Response({'status': 'error', 'message': 'Image not found.'},
                        status=status.HTTP_404_NOT_FOUND)