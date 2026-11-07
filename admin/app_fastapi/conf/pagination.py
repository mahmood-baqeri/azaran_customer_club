# utils/pagination.py
import asyncio
from urllib.parse import urlencode
from typing import Optional, Callable, Any, Dict, List, Type
from django.db.models import Model, Q, QuerySet
from django.db.models.fields import CharField, TextField, IntegerField, FloatField, DecimalField
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.db.models import JSONField
from django.http import HttpRequest
from asgiref.sync import sync_to_async
import asyncio


class PaginationService:
    """
    سرویس پیشرفته و ساده صفحه‌بندی پویا
    """

    def __init__(self, model: Type[Model], request: HttpRequest):
        self.model = model
        self.request = request
        self.params = request.query_params

        # تنظیمات پیش‌فرض
        self.page = int(self.params.get('page', 1))
        self.page_size = int(self.params.get('page_size', 12))
        self.search = self.params.get('q', '').strip()
        self.offset = (self.page - 1) * self.page_size

    async def paginate(
            self,
            base_filters: Optional[Dict] = None,
            extra_filters: Optional[Q] = None,
            order_by: Optional[List[str]] = None,
            serializer_func: Optional[Callable] = None,
            select_related: Optional[List[str]] = None,
            prefetch_related: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        صفحه‌بندی اصلی
        """
        base_filters = base_filters or {}
        extra_filters = extra_filters or Q()
        order_by = order_by or ['-created_at']

        @sync_to_async
        def execute_all():
            # 1. ساخت کوئری
            qs = self.model.objects.filter(**base_filters).filter(extra_filters)

            # 2. بهینه‌سازی
            if select_related:
                qs = qs.select_related(*select_related)
            if prefetch_related:
                qs = qs.prefetch_related(*prefetch_related)
                
            # 3. فیلتر و جستجو و مرتب‌سازی
            qs = self._apply_filters(qs)
            if self.search:
                qs = self._apply_search(qs)
            qs = self._apply_sorting(qs, order_by)

            # 4. شمارش و گرفتن آیتم‌ها
            total = qs.count()
            items = list(qs[self.offset:self.offset + self.page_size])

            # 5. سریالایز کردن (همینجا داخل sync_to_async)
            if serializer_func:
                items = [serializer_func(item) for item in items]

            return total, items

        # فقط یک بار await می‌کنیم و همه چی آماده‌ست
        total, items = await execute_all()

        # ساخت لینک‌های صفحه‌بندی
        return self._build_response(items, total)

    def _apply_filters(self, qs: QuerySet) -> QuerySet:
        """اعمال فیلترهای داینامیک از پارامترها"""
        for key, value in self.params.items():
            # رد کردن پارامترهای سیستمی
            if key in ['page', 'page_size', 'q', 'sort']:
                continue

            try:
                field = self.model._meta.get_field(key)
            except:
                continue

            # فیلتر عددی (min/max)
            if isinstance(field, (IntegerField, FloatField, DecimalField)):
                min_val = self.params.get(f'{key}_min')
                max_val = self.params.get(f'{key}_max')

                if min_val:
                    qs = qs.filter(**{f'{key}__gte': float(min_val)})
                if max_val:
                    qs = qs.filter(**{f'{key}__lte': float(max_val)})

            # فیلتر متنی
            elif isinstance(field, (CharField, TextField)):
                qs = qs.filter(**{f'{key}__icontains': value})

            # فیلتر ارتباطی (FK/M2M)
            elif isinstance(field, (ForeignKey, ManyToManyField)):
                ids = [int(x) for x in value.split(',') if x.isdigit()]
                if ids:
                    qs = qs.filter(**{f'{key}__in': ids})

            # فیلتر آرایه/JSON
            elif isinstance(field, JSONField):
                # برای JSONField ساده
                qs = qs.filter(**{f'{key}__contains': value})

        return qs

    def _apply_search(self, qs: QuerySet) -> QuerySet:
        """اعمال جستجوی کلی"""
        searchable_fields = self._get_searchable_fields()

        if not searchable_fields:
            return qs

        search_filter = Q()
        for field in searchable_fields:
            search_filter |= Q(**{f'{field}__icontains': self.search})

        return qs.filter(search_filter)

    def _get_searchable_fields(self) -> List[str]:
        """دریافت فیلدهای قابل جستجو"""
        fields = []

        # فیلدهای مستقیم
        for field in self.model._meta.fields:
            if isinstance(field, (CharField, TextField)):
                fields.append(field.name)

        # فیلدهای مرتبط محبوب
        if hasattr(self.model, 'name'):
            fields.append('name')
        if hasattr(self.model, 'title'):
            fields.append('title')
        if hasattr(self.model, 'user__first_name'):
            fields.append('user__first_name')

        return list(set(fields))

    def _apply_sorting(self, qs: QuerySet, default_order: List[str]) -> QuerySet:
        """اعمال مرتب‌سازی"""
        sort_param = self.params.get('sort')

        if not sort_param:
            return qs.order_by(*default_order)

        # نگاشت مرتب‌سازی‌های خاص
        sort_mapping = {
            'highestrated': '-review_average',
            'mostreviewed': '-review_count',
            'nameasc': 'name',
            'namedesc': '-name',
            'newest': '-created_at',
            'oldest': 'created_at',
            'priceasc': 'price',
            'pricedesc': '-price',
        }

        sort_field = sort_mapping.get(sort_param.lower(), sort_param)

        # اعتبارسنجی فیلد مرتب‌سازی
        field_name = sort_field.lstrip('-')
        if field_name in [f.name for f in self.model._meta.get_fields()]:
            return qs.order_by(sort_field)

        return qs.order_by(*default_order)

    def _build_response(self, items: List, total: int) -> Dict[str, Any]:
        """ساخت پاسخ صفحه‌بندی"""
        base_url = str(self.request.url).split('?')[0]
        query_params = dict(self.request.query_params)

        # حذف page از پارامترها
        query_params.pop('page', None)

        # لینک بعدی
        next_page = None
        if self.offset + self.page_size < total:
            query_params['page'] = self.page + 1
            next_page = f"{base_url}?{urlencode(query_params)}"

        # لینک قبلی
        previous_page = None
        if self.page > 1:
            query_params['page'] = self.page - 1
            previous_page = f"{base_url}?{urlencode(query_params)}"

        return {
            "count": total,
            "next": next_page,
            "previous": previous_page,
            "results": items,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": (total + self.page_size - 1) // self.page_size
        }


# ============================================================
# توابع کمکی ساده
# ============================================================

@sync_to_async
def get_count(queryset: QuerySet) -> int:
    """دریافت تعداد آیتم‌ها"""
    return queryset.count()


@sync_to_async
def get_slice(queryset: QuerySet, start: int, end: int) -> List:
    """دریافت برش از کوئری‌ست"""
    return list(queryset[start:end])


async def simple_paginate(
        queryset: QuerySet, request: HttpRequest, page_size: int = 10, serializer: Optional[Callable] = None) \
        -> Dict[str, Any]:
    """
    صفحه‌بندی ساده و سریع

    Args:
        queryset: کوئری‌ست اصلی
        request: درخواست
        page_size: تعداد آیتم در هر صفحه
        serializer: تابع سریالایز (اختیاری)
    """
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', page_size))

    offset = (page - 1) * page_size

    total = await get_count(queryset)
    items = await get_slice(queryset, offset, offset + page_size)

    if serializer:
        items = await asyncio.gather(*[serializer(item) for item in items])

    base_url = str(request.url).split('?')[0]
    query_params = dict(request.query_params)
    query_params.pop('page', None)

    # لینک‌ها
    next_page = None
    if offset + page_size < total:
        query_params['page'] = page + 1
        next_page = f"{base_url}?{urlencode(query_params)}"

    previous_page = None
    if page > 1:
        query_params['page'] = page - 1
        previous_page = f"{base_url}?{urlencode(query_params)}"

    return {
        "count": total,
        "next": next_page,
        "previous": previous_page,
        "results": items,
        "page": page,
        "page_size": page_size,
    }
