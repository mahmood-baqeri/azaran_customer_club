# applications/category/serializers.py

from rest_framework import serializers

from applications.category.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """سریالایزر اصلی دسته‌بندی — بدون ترجمه"""

    parent_title = serializers.SerializerMethodField()
    parent_slug = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()
    pages_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id", "title", "slug", "description",
            "parent", "parent_title", "parent_slug",
            "is_active",
            "children_count", "has_children",
            "pages_count",
        ]
        read_only_fields = ["id", "slug"]  # slug خودکار ساخته می‌شود

    def get_parent_title(self, obj):
        return obj.parent.title if obj.parent else None

    def get_parent_slug(self, obj):
        return obj.parent.slug if obj.parent else None

    def get_children_count(self, obj):
        return obj.children.count()

    def get_has_children(self, obj):
        return obj.children.exists()

    def get_pages_count(self, obj):
        return obj.pages.count()


class CategoryListSerializer(serializers.ModelSerializer):
    """سریالایزر لیست — سبک"""

    parent_title = serializers.SerializerMethodField()
    pages_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id", "title", "slug",
            "parent", "parent_title",
            "is_active", "pages_count",
        ]

    def get_parent_title(self, obj):
        return obj.parent.title if obj.parent else None

    def get_pages_count(self, obj):
        return obj.pages.count()


class CategoryTreeSerializer(serializers.ModelSerializer):
    """سریالایزر درختی"""

    children = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "title", "label", "slug", "is_active", "children"]

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        if children.exists():
            return CategoryTreeSerializer(children, many=True).data
        return []

    def get_label(self, obj):
        return f"{obj.title} ({obj.slug})"


class CategorySimpleSerializer(serializers.ModelSerializer):
    """سریالایزر ساده برای Select2 / Dropdown"""

    class Meta:
        model = Category
        fields = ["id", "title", "slug"]


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد/ویرایش — slug فقط از طریق مدل ساخته می‌شود"""

    class Meta:
        model = Category
        fields = ["id", "title", "description", "parent", "is_active"]
        read_only_fields = ["id"]

    def validate_title(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("عنوان الزامی است.")

        qs = Category.objects.filter(title=value)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("دسته‌بندی با این عنوان قبلاً وجود دارد.")

        return value

    def validate_parent(self, value):
        if not value:
            return value

        # جلوگیری از حلقه
        if self.instance and self.instance.pk:
            node = value
            while node is not None:
                if node.pk == self.instance.pk:
                    raise serializers.ValidationError(
                        "نمی‌توانید یک دسته‌بندی را والد خودش یا فرزندانش قرار دهید."
                    )
                node = node.parent
        return value


class CategoryBulkSerializer(serializers.Serializer):
    """سریالایزر عملیات دسته‌جمعی"""

    ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="لیست شناسه‌های دسته‌بندی",
    )
    action = serializers.ChoiceField(
        choices=["delete", "activate", "deactivate", "move"],
        help_text="نوع عملیات",
    )
    parent_id = serializers.IntegerField(
        required=False, allow_null=True,
        help_text="شناسه والد جدید (برای عملیات move)",
    )