# Path: applications/core/forms/use.py

# applications/product/views/web.py

from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages

# ✅ FIX: مسیر صحیح
from applications.core.forms import (
    make_input_item, make_select2_item, make_switch_item,
    make_image_item, make_file_item, make_date_item,
    make_province_city_item,
    pick_value, pick_bool,
    pick_multi_or_model, pick_switch_group_or_model,   # ← جدید
    pick_file, pick_files, require_fields,
    coerce_date, to_int,
)


def _build_items(product=None, raw_data=None):
    """raw_data = request.POST اگر POST است، وگرنه None."""
    return [
        # ─── Text / Number / Email / Textarea ────────────
        make_input_item(
            label='نام محصول', name='title',
            value=pick_value(raw_data, product, 'title'),
            required=True, col_class='col-md-6',
        ),
        make_input_item(
            label='قیمت (تومان)', name='price', kind='number',
            value=pick_value(raw_data, product, 'price', 0),
            min=0, step=1000, required=True, col_class='col-md-3',
        ),
        make_input_item(
            label='ایمیل تماس', name='contact_email', kind='email',
            value=pick_value(raw_data, product, 'contact_email'),
            col_class='col-md-3',
        ),
        make_input_item(
            label='توضیحات', name='description', kind='textarea',
            value=pick_value(raw_data, product, 'description'),
            rows=6, col_class='col-md-12',
        ),

        # ─── Select2 single + multiple ───────────────────
        make_select2_item(
            label='دسته‌بندی', name='category',
            choices=[{'id': c.pk, 'label': c.name} for c in Category.objects.all()], # type: ignore
            value=pick_value(raw_data, product, 'category_id'),
            required=True, col_class='col-md-6',
        ),
        make_select2_item(
            label='تگ‌ها', name='tags', multiple=True,
            choices=[{'id': t.pk, 'label': t.title} for t in Tag.objects.all()], # type: ignore
            # ✅ FIX: تفکیک POST خالی از GET
            value=pick_multi_or_model(raw_data, 'tags', product, 'tags'),
            col_class='col-md-6',
        ),

        # ─── Province/City ────────────────────────────────
        make_province_city_item(
            label='موقعیت',
            province_value=pick_value(raw_data, product, 'province_id'),
            city_value=pick_value(raw_data, product, 'city_id'),
            required=True,
        ),

        # ─── Dates ────────────────────────────────────────
        make_date_item(
            label='تاریخ تولید', name='manufactured_at',
            value=pick_value(raw_data, product, 'manufactured_at'),
            col_class='col-md-6',
        ),
        make_date_item(
            label='تاریخ انقضا', name='expiry_date',
            value=pick_value(raw_data, product, 'expiry_date'),
            col_class='col-md-6',
        ),

        # ─── Switch single ────────────────────────────────
        make_switch_item(
            label='فعال', name='is_active',
            value=pick_bool(raw_data, product, 'is_active', default=True),
            col_class='col-md-6',
        ),

        # ─── Switch multiple (گروه ویژگی‌ها) ─────────────
        make_switch_item(
            label='ویژگی‌ها', name='features', multiple=True,
            choices=[{'id': f.pk, 'label': f.title} for f in Feature.objects.all()], # type: ignore
            # ✅ FIX
            value=pick_switch_group_or_model(raw_data, 'features', product, 'features'),
            required=True, choice_col='col-md-3', col_class='col-md-12',
        ),

        # ─── Image single + multiple ─────────────────────
        make_image_item(
            label='تصویر اصلی', name='main_image',
            existing=product.main_image if product else None,
            col_class='col-md-6',
        ),
        make_image_item(
            label='گالری', name='gallery', multiple=True,
            existing=product.gallery.all() if product else None,
            allow_delete=bool(product),
            remove_route=(
                reverse('product:remove-gallery-image', args=[product.pk])
                if product else None
            ),
            col_class='col-md-6',
        ),

        # ─── File multiple ────────────────────────────────
        make_file_item(
            label='پیوست‌ها', name='attachments', multiple=True,
            accept='.pdf,.doc,.docx,.zip',
            files=product.attachments.all() if product else None,
            allow_delete=bool(product),
            remove_route=(
                reverse('product:remove-attachment', args=[product.pk])
                if product else None
            ),
        ),
    ]


@transaction.atomic
def _save(request, product):
    if product is None:
        product = Product() # type: ignore

    product.title         = (request.POST.get('title') or '').strip()
    product.description   = (request.POST.get('description') or '').strip()
    product.contact_email = (request.POST.get('contact_email') or '').strip()
    product.price         = to_int(request.POST.get('price')) or 0

    product.category_id = to_int(request.POST.get('category'))
    product.province_id = to_int(request.POST.get('province'))
    product.city_id     = to_int(request.POST.get('city'))

    product.is_active = pick_bool(request.POST, None, 'is_active')

    product.manufactured_at = coerce_date(request.POST.get('manufactured_at'))
    product.expiry_date     = coerce_date(request.POST.get('expiry_date'))

    cover = pick_file(request, 'main_image')
    if cover:
        product.main_image = cover

    product.save()

    # ✅ در save از pick_multi_or_model استفاده نکن — مستقیم از POST بخوان
    product.tags.set(request.POST.getlist('tags') or [])
    product.features.set(
        [k.split('#', 1)[1] for k in request.POST if k.startswith('features#')]
    )

    for img in pick_files(request, 'gallery'):
        ProductImage.objects.create(product=product, image=img) # type: ignore
    for f in pick_files(request, 'attachments'):
        ProductAttachment.objects.create(product=product, file=f) # type: ignore

    return product


def product_create(request):
    raw_data = request.POST if request.method == 'POST' else None

    if request.method == 'POST':
        missing = require_fields(request.POST, 'title', 'price', 'category', 'province')
        if missing:
            messages.error(request, f'فیلدهای الزامی: {", ".join(missing)}')
        else:
            _save(request, None)
            messages.success(request, 'محصول ایجاد شد.')
            return redirect('product:list')

    return render(request, 'layout/form.html', {'data': {
        'pageTitle': 'ایجاد محصول',
        'storeUrl':  reverse('product:create'),
        'items':     _build_items(raw_data=raw_data),
    }})


def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk) # type: ignore
    raw_data = request.POST if request.method == 'POST' else None

    if request.method == 'POST':
        missing = require_fields(request.POST, 'title', 'price', 'category', 'province')
        if missing:
            messages.error(request, f'فیلدهای الزامی: {", ".join(missing)}')
        else:
            _save(request, product)
            messages.success(request, 'تغییرات ذخیره شد.')
            return redirect('product:list')

    return render(request, 'layout/form.html', {'data': {
        'pageTitle': f'ویرایش «{product.title}»',
        'storeUrl':  reverse('product:edit', args=[pk]),
        'items':     _build_items(product=product, raw_data=raw_data),
    }})