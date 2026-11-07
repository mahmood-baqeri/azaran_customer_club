from django.db import models
from django.db.models import Case, When, IntegerField
from django.http import JsonResponse
from django.urls import reverse

from applications.user.models import User


def dt_param(request, name, default=None):
    return request.POST.get(name, request.GET.get(name, default))


def select_users(request):
    draw = int(dt_param(request, 'draw', 1))
    start = int(dt_param(request, 'start', 0))
    length = int(dt_param(request, 'length', 10))
    search_value = dt_param(request, 'search[value]', '').strip()

    # 🔹 گرفتن لیست شناسه‌های انتخاب‌شده
    selected_ids = request.POST.getlist('selected_ids[]')
    selected_ids = [int(x) for x in selected_ids if str(x).isdigit()]

    # 🔹 مرتب‌سازی
    order_column_index = int(dt_param(request, 'order[0][column]', 0))
    order_direction = dt_param(request, 'order[0][dir]', 'asc')
    columns = [
        'id',
        'first_name',
        'last_name',
        'personCode',
        'mobile',
        'nationalCode',
        'section__name',
        'unit__name',
        'actions'
    ]
    order_column = columns[order_column_index] if 0 <= order_column_index < len(columns) else 'personCode'
    if order_column == 'actions':
        order_column = 'personCode'
    if order_direction == 'desc':
        order_column = f'-{order_column}'

    # 🔹 فیلتر اولیه
    queryset = User.objects.select_related('section', 'unit').filter(is_active=1)

    section_id_filter = dt_param(request, 'section_id')
    unit_id_filter = dt_param(request, 'unit_id')
    if section_id_filter and section_id_filter.isdigit() and int(section_id_filter) > 0:
        queryset = queryset.filter(section_id=int(section_id_filter))
    if unit_id_filter and unit_id_filter.isdigit() and int(unit_id_filter) > 0:
        queryset = queryset.filter(unit_id=int(unit_id_filter))

    # 🔹 جستجو
    if search_value:
        queryset = queryset.filter(
            models.Q(first_name__icontains=search_value) |
            models.Q(last_name__icontains=search_value) |
            models.Q(username__icontains=search_value) |
            models.Q(mobile__icontains=search_value) |
            models.Q(nationalCode__icontains=search_value) |
            models.Q(personCode__icontains=search_value)
        )

    total = User.objects.filter(is_active=1).count()
    filtered = queryset.count()

    # 🔹 مرتب‌سازی: ابتدا انتخاب‌شده‌ها، سپس مرتب‌سازی عادی
    if selected_ids:
        queryset = queryset.annotate(
            is_selected=Case(
                When(id__in=selected_ids, then=1),
                default=0,
                output_field=IntegerField()
            )
        ).order_by('-is_selected', order_column)
    else:
        queryset = queryset.order_by(order_column)

    # 🔹 پیجینگ
    queryset = queryset[start:start + length]

    data = []
    for u in queryset:
        edit_url = reverse('app_user:updateUser', kwargs={'id': u.pk})
        actions_html = f"""
            <a href="{edit_url}" class="btn btn-info btn-sm" title="ویرایش">
                <i class="fas fa-edit"></i>
            </a>
        """
        data.append({
            'id': u.pk,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'personCode': u.personCode,
            'mobile': u.mobile,
            'nationalCode': u.nationalCode,
            'section': u.section.name if u.section else '-',
            'unit': u.unit.name if u.unit else '-',
            'actions': actions_html
        })

    return JsonResponse({
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': filtered,
        'data': data
    })


def users(request):
    draw = int(dt_param(request, 'draw', 1))
    start = int(dt_param(request, 'start', 0))
    length = int(dt_param(request, 'length', 10))
    search_value = dt_param(request, 'search[value]', '').strip()

    # 🔹 گرفتن لیست شناسه‌های انتخاب‌شده
    selected_ids = request.POST.getlist('selected_ids[]')
    selected_ids = [int(x) for x in selected_ids if str(x).isdigit()]

    # 🔹 مرتب‌سازی
    order_column_index = int(dt_param(request, 'order[0][column]', 0))
    order_direction = dt_param(request, 'order[0][dir]', 'asc')
    columns = [
        'first_name', 'last_name', 'personCode', 'mobile',
        'nationalCode', 'section__name', 'unit__name', 'actions'
    ]
    order_column = columns[order_column_index] if 0 <= order_column_index < len(columns) else 'personCode'
    if order_column == 'actions':
        order_column = 'personCode'
    if order_direction == 'desc':
        order_column = f'-{order_column}'

    # 🔹 فیلتر اولیه
    queryset = User.objects.select_related('section', 'unit').filter(is_active=1)

    section_id_filter = dt_param(request, 'section_id')
    unit_id_filter = dt_param(request, 'unit_id')
    if section_id_filter and section_id_filter.isdigit() and int(section_id_filter) > 0:
        queryset = queryset.filter(section_id=int(section_id_filter))
    if unit_id_filter and unit_id_filter.isdigit() and int(unit_id_filter) > 0:
        queryset = queryset.filter(unit_id=int(unit_id_filter))

    # 🔹 جستجو
    if search_value:
        queryset = queryset.filter(
            models.Q(first_name__icontains=search_value) |
            models.Q(last_name__icontains=search_value) |
            models.Q(username__icontains=search_value) |
            models.Q(mobile__icontains=search_value) |
            models.Q(nationalCode__icontains=search_value) |
            models.Q(personCode__icontains=search_value)
        )

    total = User.objects.filter(is_active=1).count()
    filtered = queryset.count()

    # 🔹 مرتب‌سازی: ابتدا انتخاب‌شده‌ها، سپس مرتب‌سازی عادی
    if selected_ids:
        queryset = queryset.annotate(
            is_selected=Case(
                When(id__in=selected_ids, then=1),
                default=0,
                output_field=IntegerField()
            )
        ).order_by('-is_selected', order_column)
    else:
        queryset = queryset.order_by(order_column)

    # 🔹 پیجینگ
    queryset = queryset[start:start + length]

    data = []
    for u in queryset:
        edit_url = reverse('app_user:updateUser', kwargs={'id': u.pk})
        actions_html = f"""
            <a href="{edit_url}" class="btn btn-info btn-sm" title="ویرایش">
                <i class="fas fa-edit"></i>
            </a>
            <button type="button" class="btn btn-sm btn-danger btnDleteRecordFromTable" data-id="{u.pk}" title="حذف">
                <i class="fas fa-trash"></i>
            </button>
        """
        data.append({
            'id': u.pk,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'personCode': u.personCode,
            'mobile': u.mobile,
            'section': u.section.name if u.section else '-',
            'unit': u.unit.name if u.unit else '-',
            'nationalCode': u.nationalCode,
            'actions': actions_html
        })

    return JsonResponse({
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': filtered,
        'data': data
    })
