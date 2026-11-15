from .helper import normalize_choices, normalize_selection


def make_select2_item(
    *, 
    label='',
    name, 
    input_id=None, 
    choices=None, 
    value=None,
    multiple=False, 
    required=False, 
    disabled=False,
    placeholder=None, 
    empty_label='— انتخاب کنید —',
    col_class='col-md-6',
):
    return {
        'b':          'select2.html',
        'c':          col_class,
        'l':          label,
        'n':          name,
        'id':         input_id or f'id_{name}',
        'data':       normalize_choices(choices),
        'v':          normalize_selection(value, multiple),
        'm':          1 if multiple else 0,
        'r':          1 if required else 0,
        'd':          1 if disabled else 0,
        'emptyLabel': empty_label if not multiple else '',
        'placeholder': placeholder or '',
    }
    
    
    
#     الف) تک‌انتخابی — ایجاد
# python
# make_select2_item(
#     label='نوع محصول',
#     name='product_type',
#     choices=[{'id': 1, 'label': 'فیزیکی'}, {'id': 2, 'label': 'دیجیتال'}],
#     required=True,
#     placeholder='نوع محصول را انتخاب کنید',
# )
# ب) تک‌انتخابی — ویرایش (مقدار از مدل)
# python
# make_select2_item(
#     label='دسته‌بندی',
#     name='category',
#     choices=Category.objects.values('id', 'name'),      # یا [{'id','label'}]
#     value=request.POST.get('category') or product.category_id,
# )
# ج) چندتایی — ایجاد
# python
# make_select2_item(
#     label='تگ‌ها',
#     name='tags',
#     choices=[{'id': t.pk, 'label': t.title} for t in Tag.objects.all()],
#     multiple=True,
#     placeholder='تگ‌ها را انتخاب کنید',
# )
# د) چندتایی — ویرایش (مقادیر از related manager)
# python
# make_select2_item(
#     label='نقش‌ها',
#     name='roles',
#     choices=[{'id': r.pk, 'label': r.name} for r in Role.objects.all()],
#     multiple=True,
#     # می‌توانی هرکدام را بدهی:
#     value=request.POST.getlist('roles')     # ← از POST (رشته‌ها)
#           or user.roles.all(),              # ← QuerySet (helper خودش pk را درمی‌آورد)
# )
# ه) غیرفعال (نمایش بدون تغییر)
# python
# make_select2_item(
#     label='وضعیت',
#     name='status',
#     choices=STATUS_CHOICES,
#     value=order.status,
#     disabled=True,
# )
# و) ترکیب با سایر کامپوننت‌ها
# python
# items = [
#     make_input_item(label='عنوان', name='title', required=True),
#     make_select2_item(
#         label='دسته',
#         name='category',
#         choices=categories,
#         value=request.POST.get('category') or obj.category_id,
#         required=True,
#     ),
#     make_select2_item(
#         label='تگ‌ها',
#         name='tags',
#         choices=tags,
#         multiple=True,
#         value=request.POST.getlist('tags') or obj.tags.all(),
#     ),
# ]
