# admin/applications/gift/repositories.py


from admin.applications.core.fileManager import uploadFile
from admin.applications.core.utils import handle_get_file, handle_get_post
from admin.applications.gift.models import Gift


def gift__store(request, item=None):
    data = {
        'text': handle_get_post(request, 'text'),
        'description':handle_get_post(request, 'description'),
        'azar_value':handle_get_post(request, 'azar_value'),
        'stock':handle_get_post(request, 'stock'),
        'photo': handle_get_file(request, 'photo'),
        'is_active': bool(handle_get_post(request, 'is_active')),
    }

    if item is None:
        item = Gift.objects.create(**data)
    else:
        for key, value in data.items():
            setattr(item, key, value)
        item.save()
        
    the_gallery = item.gallery or []
    the_gallery += [uploadFile(img) for img in request.FILES.getlist('gallery')]
    if the_gallery:
        item.gallery = the_gallery
    item.save()

    return item