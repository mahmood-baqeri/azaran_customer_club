# applications/category/drf.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q

from applications.category.models import Category
from applications.category.serializers import (
    CategorySerializer,
    CategoryListSerializer,
    CategoryTreeSerializer,
    CategorySimpleSerializer,
    CategoryCreateUpdateSerializer,
    CategoryBulkSerializer,
)
from applications.category.filters import CategoryFilter


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet مدیریت دسته‌بندی‌ها — بدون ترجمه"""

    queryset = Category.objects.all().select_related("parent")
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CategoryFilter
    search_fields = ["title", "slug", "description"]
    ordering_fields = ["id", "title", "slug", "is_active"]
    ordering = ["title"]

    # ---------------------------------------------------------
    # Permissions
    # ---------------------------------------------------------
    def get_permissions(self):
        if self.action in ["list", "retrieve", "tree", "simple", "children", "stats"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    # ---------------------------------------------------------
    # Serializer
    # ---------------------------------------------------------
    def get_serializer_class(self):
        if self.action == "list":
            return CategoryListSerializer
        if self.action == "retrieve":
            return CategorySerializer
        if self.action == "create" or self.action == "update" or self.action == "partial_update":
            return CategoryCreateUpdateSerializer
        if self.action == "tree":
            return CategoryTreeSerializer
        if self.action == "simple":
            return CategorySimpleSerializer
        if self.action == "bulk_action":
            return CategoryBulkSerializer
        return CategorySerializer

    # ---------------------------------------------------------
    # Queryset
    # ---------------------------------------------------------
    def get_queryset(self):
        queryset = super().get_queryset()
        # کاربر مهمان فقط دسته‌های فعال را ببیند
        if self.action in ["list", "retrieve", "tree"]:
            if not self.request.user.is_authenticated:
                queryset = queryset.filter(is_active=True)
        return queryset

    # ---------------------------------------------------------
    # tree
    # ---------------------------------------------------------
    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
        """درخت کامل دسته‌بندی‌ها"""
        roots = self.get_queryset().filter(parent__isnull=True)
        serializer = CategoryTreeSerializer(roots, many=True)
        return Response({"status": "success", "data": serializer.data})

    # ---------------------------------------------------------
    # simple
    # ---------------------------------------------------------
    @action(detail=False, methods=["get"], url_path="simple")
    def simple(self, request):
        """لیست ساده برای Select2"""
        queryset = self.get_queryset().filter(is_active=True)

        parent_id = request.query_params.get("parent")
        if parent_id:
            if parent_id in ("null", "0", "root"):
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent_id)

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(slug__icontains=search)
            )

        limit = request.query_params.get("limit")
        try:
            limit = int(limit) if limit else 0
        except ValueError:
            limit = 0

        if limit > 0:
            queryset = queryset[:limit]

        serializer = CategorySimpleSerializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data})

    # ---------------------------------------------------------
    # children
    # ---------------------------------------------------------
    @action(detail=True, methods=["get"], url_path="children")
    def children(self, request, pk=None):
        """زیردسته‌های یک دسته"""
        category = self.get_object()
        children = category.children.filter(is_active=True)
        serializer = CategorySimpleSerializer(children, many=True)
        return Response({"status": "success", "data": serializer.data})

    # ---------------------------------------------------------
    # parents (مسیر تا ریشه)
    # ---------------------------------------------------------
    @action(detail=True, methods=["get"], url_path="parents")
    def parents(self, request, pk=None):
        """والدین یک دسته تا ریشه"""
        category = self.get_object()
        parents = []
        current = category.parent
        while current:
            parents.append({
                "id": current.id,
                "title": current.title,
                "slug": current.slug,
            })
            current = current.parent
        return Response({"status": "success", "data": parents})

    # ---------------------------------------------------------
    # toggle-status
    # ---------------------------------------------------------
    @action(detail=True, methods=["post"], url_path="toggle-status")
    def toggle_status(self, request, pk=None):
        category = self.get_object()
        category.is_active = not category.is_active
        category.save(update_fields=["is_active"])
        return Response({
            "status": "success",
            "is_active": category.is_active,
            "message": f"وضعیت به {'فعال' if category.is_active else 'غیرفعال'} تغییر یافت",
        })

    # ---------------------------------------------------------
    # bulk_action
    # ---------------------------------------------------------
    @action(detail=False, methods=["post"], url_path="bulk-action")
    def bulk_action(self, request):
        serializer = CategoryBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data["ids"]
        action_value = serializer.validated_data["action"]

        queryset = Category.objects.filter(id__in=ids)

        if action_value == "delete":
            # جلوگیری از حذف دسته‌هایی که page یا children دارند
            for cat in queryset:
                if cat.pages.exists():
                    return Response(
                        {"status": "error", "message": f"دسته «{cat.title}» دارای صفحه است"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if cat.children.exists():
                    return Response(
                        {"status": "error", "message": f"دسته «{cat.title}» دارای زیردسته است"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            count = queryset.count()
            queryset.delete()
            return Response({"status": "success", "message": f"{count} دسته‌بندی حذف شدند"})

        if action_value == "activate":
            count = queryset.update(is_active=True)
            return Response({"status": "success", "message": f"{count} دسته‌بندی فعال شدند"})

        if action_value == "deactivate":
            count = queryset.update(is_active=False)
            return Response({"status": "success", "message": f"{count} دسته‌بندی غیرفعال شدند"})

        if action_value == "move":
            parent_id = serializer.validated_data.get("parent_id")
            # چک حلقه: هر دسته نباید زیرمجموعه‌ی خودش شود
            if parent_id:
                target = Category.objects.filter(pk=parent_id).first()
                if not target:
                    return Response(
                        {"status": "error", "message": "والد یافت نشد"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                # اگر یکی از ids در زیردرخت target باشد → حلقه
                for cat in queryset:
                    node = target
                    while node is not None:
                        if node.pk == cat.pk:
                            return Response(
                                {"status": "error",
                                 "message": f"دسته «{cat.title}» نمی‌تواند زیرمجموعه‌ی خودش شود"},
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                        node = node.parent

            count = queryset.update(parent_id=parent_id)
            return Response({"status": "success", "message": f"{count} دسته‌بندی جابه‌جا شدند"})

        return Response(
            {"status": "error", "message": "عملیات نامعتبر"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ---------------------------------------------------------
    # stats
    # ---------------------------------------------------------
    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        total = Category.objects.count()
        active = Category.objects.filter(is_active=True).count()
        inactive = total - active
        root = Category.objects.filter(parent__isnull=True).count()

        has_children = (
            Category.objects.filter(children__isnull=False)
            .distinct()
            .count()
        )

        with_pages = (
            Category.objects.filter(pages__isnull=False)
            .distinct()
            .count()
        )

        # توزیع دسته‌ها بر اساس تعداد صفحات (top 5)
        top_by_pages = (
            Category.objects.annotate(c=Count("pages"))
            .filter(c__gt=0)
            .order_by("-c")[:5]
            .values("id", "title", "c")
        )

        return Response({
            "status": "success",
            "data": {
                "total": total,
                "active": active,
                "inactive": inactive,
                "root_categories": root,
                "categories_with_children": has_children,
                "categories_with_pages": with_pages,
                "max_depth": self._get_max_depth(),
                "top_by_pages": list(top_by_pages),
            },
        })

    def _get_max_depth(self):
        """محاسبه عمق درخت (بدون N+1 با پیمایش ساده)"""
        categories = list(Category.objects.values("id", "parent_id"))
        by_id = {c["id"]: c["parent_id"] for c in categories}

        max_depth = 0
        for cat_id in by_id:
            depth = 0
            current = by_id.get(cat_id)
            guard = 0
            while current is not None and guard < 100:
                depth += 1
                current = by_id.get(current)
                guard += 1
            max_depth = max(max_depth, depth)
        return max_depth