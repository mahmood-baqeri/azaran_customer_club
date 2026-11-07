from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count

from applications.page.models import Page
from applications.page.serializers import (
    PageListSerializer,
    PageDetailSerializer,
    PageCreateUpdateSerializer,
    PageBulkSerializer,
)
from applications.page.filters import PageFilter


class PageViewSet(viewsets.ModelViewSet):
    """ViewSet ساده برای صفحات"""

    queryset = Page.objects.all().select_related("category")
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PageFilter
    search_fields = ["title", "summer", "text", "slug"]
    ordering_fields = ["id", "title", "slug", "type", "is_active", "created"]
    ordering = ["-id"]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "simple"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [perm() for perm in permission_classes]

    def get_serializer_class(self):
        if self.action == "list":
            return PageListSerializer
        elif self.action == "retrieve":
            return PageDetailSerializer
        elif self.action == "simple":
            return PageListSerializer
        elif self.action == "bulk_action":
            return PageBulkSerializer
        return PageCreateUpdateSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ["list", "retrieve"] and not self.request.user.is_authenticated:
            queryset = queryset.filter(is_active=True)
        return queryset

    # ---------------------------------------------------------
    # لیست ساده برای Select2 / Dropdown
    # ---------------------------------------------------------
    @action(detail=False, methods=["get"], url_path="simple")
    def simple(self, request):
        queryset = self.get_queryset().filter(is_active=True)

        category_id = request.query_params.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        type_filter = request.query_params.get("type")
        if type_filter:
            queryset = queryset.filter(type=type_filter)

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(slug__icontains=search)
            )

        limit = request.query_params.get("limit", 50)
        try:
            limit = int(limit)
        except ValueError:
            limit = 50

        serializer = self.get_serializer(queryset[:limit], many=True)
        return Response({"status": "success", "data": serializer.data})

    # ---------------------------------------------------------
    # آمار ساده
    # ---------------------------------------------------------
    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        pages = Page.objects.all()
        data = {
            "total": pages.count(),
            "active": pages.filter(is_active=True).count(),
            "inactive": pages.filter(is_active=False).count(),
            "by_type": {},
            "by_category": {},
        }

        for type_code, _label in Page.PageType.choices:
            data["by_type"][type_code] = pages.filter(type=type_code).count()

        data["by_category"] = {
            row["category__title"]: row["count"]
            for row in pages.filter(category__isnull=False)
            .values("category__title")
            .annotate(count=Count("id"))
        }

        return Response({"status": "success", "data": data})

    # ---------------------------------------------------------
    # تغییر وضعیت
    # ---------------------------------------------------------
    @action(detail=True, methods=["post"], url_path="toggle-status")
    def toggle_status(self, request, pk=None):
        page = self.get_object()
        page.is_active = not page.is_active
        page.save(update_fields=["is_active"])
        return Response(
            {
                "status": "success",
                "is_active": page.is_active,
                "message": f"وضعیت به {'فعال' if page.is_active else 'غیرفعال'} تغییر یافت",
            }
        )

    # ---------------------------------------------------------
    # عملیات دسته‌جمعی
    # ---------------------------------------------------------
    @action(detail=False, methods=["post"], url_path="bulk-action")
    def bulk_action(self, request):
        serializer = PageBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data["ids"]
        action_value = serializer.validated_data["action"]

        queryset = Page.objects.filter(id__in=ids)

        actions_map = {
            "delete": lambda q: q.delete(),
            "activate": lambda q: q.update(is_active=True),
            "deactivate": lambda q: q.update(is_active=False),
        }
        messages_map = {
            "delete": "صفحه حذف شدند",
            "activate": "صفحه فعال شدند",
            "deactivate": "صفحه غیرفعال شدند",
        }

        if action_value not in actions_map:
            return Response(
                {"status": "error", "message": "عملیات نامعتبر"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = actions_map[action_value](queryset)
        count = result if isinstance(result, int) else queryset.count()
        return Response(
            {"status": "success", "message": f"{count} {messages_map.get(action_value, 'انجام شد')}"}
        )