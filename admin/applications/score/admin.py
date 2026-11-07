from django.contrib import admin

from applications.score.models import ScoreRule, UserScore, UserScoreLog


@admin.register(ScoreRule)
class ScoreRuleAdmin(admin.ModelAdmin):
    list_display = (
        "code", "calc_type", "default_amount",
        "cap_period", "cap_count", "requires_approval", "is_active",
    )
    list_filter = ("calc_type", "cap_period", "is_active", "requires_approval")
    search_fields = ("code",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("شناسه", {"fields": ("code", "is_active", "priority")}),
        ("مقدار", {"fields": ("calc_type", "default_amount")}),
        ("محدودیت", {"fields": ("cap_period", "cap_count", "max_amount_per_period")}),
        ("شرط", {"fields": ("requires_reference", "requires_approval")}),
        ("بازه اعتبار", {"fields": ("valid_from", "valid_until")}),
        ("متادیتا", {"fields": ("metadata",)}),
    )


@admin.register(UserScore)
class UserScoreAdmin(admin.ModelAdmin):
    list_display = ("user", "current_balance", "total_earned", "total_spent", "updated_at")
    search_fields = ("user__mobile", "user__username", "user__first_name", "user__last_name")
    raw_id_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(UserScoreLog)
class UserScoreLogAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "transaction_code", "direction",
        "amount", "balance_after", "source", "created_at",
    )
    list_filter = ("transaction_code", "direction", "source", "is_reversed")
    search_fields = ("user__mobile", "reference_id", "idempotency_key", "reason")
    raw_id_fields = ("user", "created_by", "reverses_log")
    date_hierarchy = "created_at"

    # لاگ‌ها تغییرناپذیرند
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False