from rest_framework import serializers

from applications.page.models import Page


class PageListSerializer(serializers.ModelSerializer):
    """سریالایزر لیست صفحات — سبک"""

    category_title = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = [
            "id", "title", "summer", "slug", "type",
            "category", "category_title",
            "photo",
            "is_active", "created",
        ]

    def get_category_title(self, obj):
        return obj.category.title if obj.category else None


class PageDetailSerializer(serializers.ModelSerializer):
    """سریالایزر جزئیات صفحه"""

    category_title = serializers.SerializerMethodField()
    category_slug = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = [
            "id", "title", "summer", "text", "slug", "type",
            "category", "category_title", "category_slug",
            "photo", "gallery",
            "is_active", "created",
        ]

    def get_category_title(self, obj):
        return obj.category.title if obj.category else None

    def get_category_slug(self, obj):
        return obj.category.slug if obj.category else None


class PageCreateUpdateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد/ویرایش — کاربر نمی‌تواند slug بفرستد"""

    class Meta:
        model = Page
        fields = [
            "id", "title", "summer", "text", "type",
            "category", "photo", "gallery", "is_active",
        ]
        read_only_fields = ["id"]

    def validate_title(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("عنوان الزامی است.")
        return value


class PageBulkSerializer(serializers.Serializer):
    """عملیات دسته‌جمعی"""

    ids = serializers.ListField(
        child=serializers.IntegerField(), help_text="لیست شناسه‌های صفحه"
    )
    action = serializers.ChoiceField(
        choices=[
            "delete",
            "activate",
            "deactivate",
        ],
        help_text="نوع عملیات",
    )