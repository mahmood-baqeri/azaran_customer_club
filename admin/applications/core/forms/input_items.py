# Path: applications/core/forms/input_items.py

# applications/core/forms/input_items.py

from datetime import date, datetime

def _format_for_kind(value, kind):
    """مقدار مدل را به فرمت صحیح input تبدیل می‌کند."""
    if value is None or value == '':
        return ''

    if kind == 'datetime-local':
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%dT%H:%M')
        if isinstance(value, str):
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M',
                        '%Y-%m-%dT%H:%M:%S'):
                try:
                    return datetime.strptime(value, fmt).strftime('%Y-%m-%dT%H:%M')
                except ValueError:
                    continue
            return value  # از POST آمده — همان فرمت مرورگر
        return str(value)

    if kind == 'date':
        if isinstance(value, (datetime, date)):
            return value.strftime('%Y-%m-%d')
        return str(value)

    if kind == 'time':
        if isinstance(value, datetime):
            return value.strftime('%H:%M')
        return str(value)

    return value

def make_input_item(
    *,
    label='',
    name,
    input_id=None,
    value=None,
    kind='text',                # 'text' | 'email' | 'number' | 'password' | 'textarea' | 'tel' | 'url'
    required=False,
    disabled=False,
    readonly=False,
    placeholder=None,
    autocomplete=None,
    rows=5,
    col_class='col-md-6',
    **extra,                    # min, max, step, maxlength, pattern, ...
):
    if autocomplete is None:
        autocomplete = 'off' if kind == 'password' else ''

    item = {
        'b':    'input.html',
        'c':    col_class,
        'l':    label,
        'n':    name,
        'id':   input_id or f'id_{name}',
        't':    kind,
        'v':    _format_for_kind(value, kind),
        'r':    1 if required else 0,
        'd':    1 if disabled else 0,
        'ro':   1 if readonly else 0,
        'pl':   placeholder or '',
        'ac':   autocomplete,
        'rows': rows,
    }
    item.update(extra)
    return item







# ۳) نمونه‌های فراخوانی

# data = {
#     'pageTitle': 'ایجاد محصول',
#     'storeUrl':  reverse('app_product:create'),
#     'items': [
#         make_input_item(
#             label='نام محصول',
#             name='title',
#             kind='text',
#             value=request.POST.get('title') or '',
#             required=True,
#             col_class='col-md-6',
#         ),
#         make_input_item(
#             label='قیمت (تومان)',
#             name='price',
#             kind='number',
#             value=request.POST.get('price') or 0,
#             required=True,
#             min=0,
#             step=1000,
#             col_class='col-md-6',
#         ),
#         make_input_item(
#             label='ایمیل تماس',
#             name='contact_email',
#             kind='email',
#             value=request.POST.get('contact_email') or product.contact_email,
#             col_class='col-md-6',
#         ),
#         make_input_item(
#             label='رمز عبور',
#             name='password',
#             kind='password',
#             required=True,
#             col_class='col-md-6',
#         ),
#         make_input_item(
#             label='توضیحات',
#             name='description',
#             kind='textarea',
#             value=request.POST.get('description') or product.description,
#             placeholder='توضیحات کامل محصول را وارد کنید…',
#             rows=6,
#             col_class='col-md-12',
#         ),
#         # فیلد فقط-خواندنی (مقدار ارسال می‌شود)
#         make_input_item(
#             label='کد محصول',
#             name='sku',
#             kind='text',
#             value=product.sku,
#             readonly=True,
#             col_class='col-md-6',
#         ),
#         # فیلد غیرفعال (مقدار ارسال نمی‌شود)
#         make_input_item(
#             label='تاریخ ثبت',
#             name='created_at_display',
#             kind='text',
#             value=product.created_at.strftime('%Y-%m-%d'),
#             disabled=True,
#             col_class='col-md-6',
#         ),
#     ],
# }
# return render(request, 'layout/form.html', {'data': data})