# from django.core.cache import cache
# from applications.language.models import Language
#
#
# class LanguageCacheMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         languages = cache.get('languages_list')
#
#         if not languages:
#             languages = [(lang.code, lang.name) for lang in Language.objects.filter(is_active=1)]
#             cache.set('languages_list', languages, timeout=None)
#             print(f"✅ کش مقداردهی شد: {languages}")  # بررسی مقدار ذخیره‌شده
#
#         response = self.get_response(request)
#         return response
