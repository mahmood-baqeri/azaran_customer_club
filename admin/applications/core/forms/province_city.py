from .helper import to_int
from applications.setting.models import Province, City


def make_province_city_item(
    *,
    label='',
    province_name='province',
    city_name='city',
    province_id='id_province',
    city_id='id_city',
    province_value=None, 
    city_value=None,
    required=False, 
    col_class='col-md-12',
):
    province_value = to_int(province_value)
    city_value = to_int(city_value)

    provinces = Province.objects.all().order_by('name')
    cities = (
        City.objects.filter(province_id=province_value).order_by('name')
        if province_value else City.objects.none()
    )
    return {
        'b': 'province_city.html',
        'l': label,
        'c': col_class,
        'r': 1 if required else 0,
        'provinceName': province_name,
        'cityName': city_name,
        'provinceID': province_id,
        'cityID': city_id,
        'provinceValue': province_value,
        'cityValue': city_value,
        'provinces': [{'id': p.pk, 'label': p.name} for p in provinces],
        'cities':    [{'id': c.pk, 'label': c.name} for c in cities],
    }
    
    


#  'items': [
#             make_province_city_item(
#                 label='محل سکونت',
#                 province_value=province_value,
#                 city_value=city_value,
#                 required=True,
#             ),
#         ],

#    items = [
#         make_province_city_item(
#             label='موقعیت شعبه',
#             province_value=province_value,
#             city_value=city_value,
#             required=True,
#         ),
#     ]


# def edit_profile(request):
#     user = request.user
#     items = [
#         make_province_city_item(
#             label='محل سکونت',
#             province_value=request.POST.get('province') or user.province_id,
#             city_value=request.POST.get('city')         or user.city_id,
#             required=True,
#         ),
#     ]
#     data = {
#         'pageTitle': 'ویرایش پروفایل',
#         'storeUrl':  reverse('app_user:edit_profile'),
#         'items':     items,
#     }
#     return render(request, 'layout/form.html', {'data': data})