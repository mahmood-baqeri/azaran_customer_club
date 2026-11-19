# Path: applications/core/forms/date_item.py

from .helper import coerce_date


def make_date_item(
    *,
    label='',
    name='date',
    input_id=None,
    value=None,
    required=False, 
    disabled=False,
    col_class='col-md-6',
):
    value = coerce_date(value)
    return {
        'b':           'date.html',
        'l':           label,
        'c':           col_class,
        'n':           name,
        'id':          input_id or f'id_{name}',
        'v':           value,
        'hiddenValue': value.strftime('%Y-%m-%d') if value else '',
        'r':           1 if required else 0,
        'd':           1 if disabled else 0,
    }
    
    
#  الف) فرم ایجاد — بدون مقدار اولیه
# from applications.core.utils.forms import make_date_item

# def create_event(request):
#     data = {
#         'pageTitle': 'ثبت رویداد',
#         'storeUrl':  reverse('app_event:create'),
#         'items': [
#             make_date_item(
#                 label='تاریخ شروع',
#                 name='start_date',
#                 required=True,
#             ),
#             make_date_item(
#                 label='تاریخ پایان',
#                 name='end_date',
#                 required=False,
#                 col_class='col-md-6',
#             ),
#         ],
#     }
#     return render(request, 'layout/form.html', {'data': data})



# ب) فرم ویرایش — مقدار اولیه از مدل
# def edit_event(request, pk):
#     event = get_object_or_404(Event, pk=pk)

#     start_value = request.POST.get('start_date') or event.start_date
#     end_value   = request.POST.get('end_date')   or event.end_date

#     data = {
#         'pageTitle': 'ویرایش رویداد',
#         'storeUrl':  reverse('app_event:edit', args=[pk]),
#         'items': [
#             make_date_item(
#                 label='تاریخ شروع',
#                 name='start_date',
#                 value=start_value,
#                 required=True,
#             ),
#             make_date_item(
#                 label='تاریخ پایان',
#                 name='end_date',
#                 value=end_value,
#             ),
#         ],
#     }
#     return render(request, 'layout/form.html', {'data': data})


# ج) پیش‌فرض امروز
# from datetime import date

# make_date_item(
#     label='تاریخ ثبت',
#     name='register_date',
#     value=date.today(),
#     required=True,
# )