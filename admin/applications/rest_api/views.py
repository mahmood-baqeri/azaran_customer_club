import json
import math
import uuid
from datetime import datetime, timedelta

from django.db.models import Q
from django.http import JsonResponse

from applications.core.decorators import authentication_required
from applications.core.processors import initAppSetting
from applications.setting.models import Setting

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings
from django.core.files.storage import default_storage


def citiesOfState(request):
    if request.method == 'POST':
        inputData = json.loads(request.body)
        # cities = City.objects.filter(state_id=inputData['param']['id'])
        # responseData = []
        # for item in cities:
        #     newItem = {
        #         'id': item.pk,
        #         'name': item.name,
        #     }
        #     responseData.append(newItem)
        # return JsonResponse({"data": responseData}, content_type="application/json", status=201)


###############################################################################
###############################################################################
###############################################################################    Upload Image
@authentication_required
@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']

        # نام فایل و مسیر ذخیره‌سازی
        file_name = uploaded_file.name
        file_path = os.path.join(settings.MEDIA_ROOT, 'tinymce_uploads', file_name)

        # ذخیره فایل
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        file_url = default_storage.save(file_path, uploaded_file)

        # ساخت URL دسترسی به فایل
        file_url = request.build_absolute_uri(settings.MEDIA_URL + 'tinymce_uploads/' + file_name)

        return JsonResponse({'location': file_url})

    return JsonResponse({'error': 'File not uploaded'}, status=400)


@authentication_required
def get_uploaded_images(request):
    media_path = os.path.join(settings.MEDIA_ROOT, 'tinymce_uploads')
    if not os.path.exists(media_path):
        return JsonResponse({'images': []})

    images = []
    for file_name in os.listdir(media_path):
        file_url = request.build_absolute_uri(settings.MEDIA_URL + 'tinymce_uploads/' + file_name)
        images.append({'name': file_name, 'url': file_url})

    return JsonResponse({'images': images})


@authentication_required
@csrf_exempt
def delete_image(request):
    if request.method == 'POST':
        image_name = request.POST.get('image_name')
        image_path = os.path.join(settings.MEDIA_ROOT, 'tinymce_uploads', image_name)

        if os.path.exists(image_path):
            os.remove(image_path)
            return JsonResponse({'status': 'success', 'message': 'Image deleted successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Image not found.'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)