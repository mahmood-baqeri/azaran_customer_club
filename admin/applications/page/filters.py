from django_filters import rest_framework as filters
from django.db.models import Q

from applications.page.models import Page


class PageFilter(filters.FilterSet):
    """فیلترهای DRF برای صفحات"""

    search = filters.CharFilter(method="filter_search", label="جستجو")

    category = filters.NumberFilter(field_name="category", lookup_expr="exact")
    category__in = filters.BaseInFilter(field_name="category", lookup_expr="in")

    type = filters.CharFilter(field_name="type", lookup_expr="exact")
    type__in = filters.BaseInFilter(field_name="type", lookup_expr="in")

    is_active = filters.BooleanFilter()

    created_after = filters.DateTimeFilter(field_name="created", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created", lookup_expr="lte")

    ordering = filters.OrderingFilter(
        fields=(
            ("id", "id"),
            ("title", "title"),
            ("slug", "slug"),
            ("type", "type"),
            ("is_active", "is_active"),
            ("created", "created"),
            ("updated", "updated"),
        ),
        field_labels={
            "id": "شناسه",
            "title": "عنوان",
            "slug": "اسلاگ",
            "type": "نوع",
            "is_active": "وضعیت",
            "created": "تاریخ ایجاد",
            "updated": "تاریخ بروزرسانی",
        },
    )

    class Meta:
        model = Page
        fields = [
            "search",
            "category", "category__in",
            "type", "type__in",
            "is_active",
            "created_after", "created_before",
        ]

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(title__icontains=value)
                | Q(summer__icontains=value)
                | Q(text__icontains=value)
                | Q(slug__icontains=value)
                | Q(category__title__icontains=value)
            ).distinct()
        return queryset