# applications/factor/admin.py

from django.contrib import admin

from applications.factor.models import Factor


@admin.register(Factor)
class FactorAdmin(admin.ModelAdmin):
    list_display = (
        "id", "invoice_number", "user", "status",
        "amount", "shop_name", "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "invoice_number", "user__mobile", "user__first_name",
        "user__last_name", "shop_name", "seller_phone",
    )
    raw_id_fields = ("user", "approved_by")
    readonly_fields = ("approved_at", "rejected_at", "created_at", "updated_at")
    date_hierarchy = "created_at"

    fieldsets = (
        ("هویت", {
            "fields": ("user", "invoice_number", "status", "photo"),
        }),
        ("اطلاعات فاکتور", {
            "fields": ("amount", "invoice_issue_at"),
        }),
        ("متره", {
            "fields": (
                "number_water_taps", "number_connections", "pipe_length",
            ),
        }),
        ("فروشگاه", {
            "fields": ("shop_name", "seller_phone", "seller_address"),
        }),
        ("Audit", {
            "fields": (
                "approved_by", "approved_at",
                "rejected_at", "rejection_reason",
            ),
        }),
    )