# applications/category/filters.py

from django_filters import rest_framework as filters
from django.db.models import Q

from applications.category.models import Category


class CategoryFilter(filters.FilterSet):
    """فیلترهای DRF برای دسته‌بندی"""

    search = filters.CharFilter(method="filter_search", label="جستجو")

    parent = filters.NumberFilter(field_name="parent", lookup_expr="exact")
    parent__isnull = filters.BooleanFilter(field_name="parent", lookup_expr="isnull")

    is_active = filters.BooleanFilter()

    ordering = filters.OrderingFilter(
        fields=(
            ("id", "id"),
            ("title", "title"),
            ("slug", "slug"),
            ("is_active", "is_active"),
        ),
        field_labels={
            "id": "شناسه",
            "title": "عنوان",
            "slug": "اسلاگ",
            "is_active": "وضعیت",
        },
    )

    class Meta:
        model = Category
        fields = ["search", "parent", "parent__isnull", "is_active"]

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(title__icontains=value)
                | Q(slug__icontains=value)
                | Q(description__icontains=value)
            ).distinct()
        return queryset