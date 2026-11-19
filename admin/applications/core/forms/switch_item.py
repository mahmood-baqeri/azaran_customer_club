# Path: applications/core/forms/switch_item.py

from .helper import normalize_choices, normalize_selection, to_bool


def make_switch_item(
    *,
    label='',
    name,
    input_id=None,
    value=None,              # single: 1/0/'on'/'1'/True/False | multiple: list of ids
    choices=None,            # فقط برای multiple
    multiple=False,
    required=False,          # single: چک‌باکس اجباری | multiple: «حداقل یکی» (با JS)
    disabled=False,
    value_on='on',           # مقدار ارسالی وقتی روشن است
    col_class='col-md-12',
    choice_col='col-md-6',
):
    base = {
            'b': 'switch.html',
            'c': col_class,
            'l': label,
            'n': name,
            'id': input_id or f'id_{name}',
            'm': 1 if multiple else 0,
            'r': 1 if required else 0,
            'd': 1 if disabled else 0,
        }
    if multiple:
        base.update({
            'choices':   normalize_choices(choices),
            'selected':  normalize_selection(value, multiple=True),
            'choiceCol': choice_col,
        })
    else:
        base.update({
            'checked': to_bool(value),
            'valueOn': value_on,
        })
    return base








# ۳) نمونه‌های فراخوانی
# الف) سوئیچ تک — ایجاد (پیش‌فرض خاموش)
# python
# make_switch_item(
#     label='فعال باشد',
#     name='is_active',
#     required=True,
#     col_class='col-md-6',
# )
# ب) سوئیچ تک — ویرایش (مقدار از مدل boolean)
# python
# make_switch_item(
#     label='فعال باشد',
#     name='is_active',
#     value=request.POST.get('is_active') or obj.is_active,   # True/False
#     col_class='col-md-6',
# )
# ج) سوئیچ تک با مقدار ارسالی دلخواه
# python
# make_switch_item(
#     label='موافقت با قوانین',
#     name='accept_terms',
#     value_on='1',        # به‌جای 'on' مقدار '1' ارسال شود
#     required=True,
# )
# د) سوئیچ تک — فقط‌نمایشی
# python
# make_switch_item(
#     label='تأیید مدیر',
#     name='manager_approved',
#     value=obj.manager_approved,
#     disabled=True,
# )
# ه) گروه سوئیچ — ایجاد
# python
# make_switch_item(
#     label='دسترسی‌ها',
#     name='permissions',
#     choices=[
#         {'id': 1, 'label': 'مشاهده'},
#         {'id': 2, 'label': 'ایجاد'},
#         {'id': 3, 'label': 'ویرایش'},
#         {'id': 4, 'label': 'حذف'},
#     ],
#     multiple=True,
#     required=True,               # حداقل یکی
#     choice_col='col-md-3',
# )
# و) گروه سوئیچ — ویرایش (مقادیر از related manager)
# python
# make_switch_item(
#     label='نقش‌ها',
#     name='roles',
#     choices=[{'id': r.pk, 'label': r.name} for r in Role.objects.all()],
#     multiple=True,
#     value=request.POST.getlist('roles') or user.roles.all(),
#     choice_col='col-md-4',
# )
# ز) دو گروه در یک صفحه (id یکتا)
# python
# items = [
#     make_switch_item(
#         label='دسترسی‌های عمومی',
#         name='public_perms',
#         input_id='id_public_perms',
#         choices=public_choices,
#         multiple=True,
#     ),
#     make_switch_item(
#         label='دسترسی‌های مدیریتی',
#         name='admin_perms',
#         input_id='id_admin_perms',
#         choices=admin_choices,
#         multiple=True,
#         required=True,
#     ),
# ] 









# ۴) پردازش سمت View
# single (بدون تغییر نسبت به قبل)
# python
# # POST: is_active='on' (چک‌شده) یا اصلاً وجود ندارد (چک‌نشده)
# is_active = request.POST.get('is_active') == 'on'
# اگر value_on='1' ست کرده باشی:

# python
# is_active = request.POST.get('is_active') == '1'
# برای اطمینان، از همان helper استفاده کن:

# python
# from applications.core.utils.forms import _to_bool
# is_active = _to_bool(request.POST.get('is_active'))
# multiple (نام با # جداشده)
# اگر می‌خواهی همان قرارداد name#id را نگه داری:

# python
# def collect_group_selections(request, name):
#     """{'perm': ['1','3','4']} از POST استخراج می‌کند."""
#     return [k.split('#', 1)[1] for k in request.POST if k.startswith(f'{name}#')]
# استفاده:

# python
# selected_perms = collect_group_selections(request, 'permissions')
# user.permissions.set(selected_perms)
# اگر قرارداد name
# #id
#  را دوست نداری، می‌توانی به name (بدون 
# #
# ) مهاجرت کنی و از request.POST.getlist('permissions') استفاده کنی — ولی آن تغییر بزرگ‌تری است. برای سازگاری، همان # را نگه می‌داریم.