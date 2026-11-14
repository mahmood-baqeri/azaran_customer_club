# applications/promotion/forms.py

from django import forms

from .models import Promotion, PromotionItem, PromotionOrder


# ═══════════════════════════════════════════════════════════
# Action Forms
# ═══════════════════════════════════════════════════════════
class OrderStatusForm(forms.Form):
    new_status = forms.ChoiceField(
        choices=PromotionOrder.Status.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    tracking_code = forms.CharField(
        required=False, max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )


class OrderAssignForm(forms.Form):
    assigned_to = forms.ModelChoiceField(
        queryset=None, required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from applications.user.models import User
        self.fields["assigned_to"].queryset = User.objects.filter(
            is_staff=True, is_active=True
        ).order_by("first_name", "last_name")


# ═══════════════════════════════════════════════════════════
# PROMOTION FORM
# ═══════════════════════════════════════════════════════════
def promotion__form(promotion=None, raw_data=None):
    """items برای قالب عمومی form.html"""

    def val(field, default=""):
        if raw_data is not None:
            return raw_data.get(field, default)
        if promotion is not None:
            return getattr(promotion, field, default)
        return default

    def is_active_value():
        if raw_data is not None:
            return 1 if str(raw_data.get("is_active", "")).lower() in ("on", "true", "1") else 0
        if promotion is not None:
            return 1 if promotion.is_active else 0
        return 1  # پیش‌فرض: فعال

    return [
        {
            "l": "عنوان پک *",
            "n": "title",
            "v": val("title"),
            "id": "the_title",
            "r": True,
            "c": "col-md-9",
            "b": "textBox.html",
        },
        {
            "l": "فعال",
            "n": "is_active",
            "v": is_active_value(),
            "id": "is_active",
            "r": None,
            "c": "col-md-3",
            "b": "switch.html",
        },
    ]


# ═══════════════════════════════════════════════════════════
# PROMOTION ITEM FORM
# ═══════════════════════════════════════════════════════════
def promotion_item__form(item=None, raw_data=None):
    """items برای قالب عمومی form.html — آیتم داخل پک"""

    def val(field, default=""):
        if raw_data is not None:
            return raw_data.get(field, default)
        if item is not None:
            return getattr(item, field, default)
        return default

    def photo_url():
        if not item or not item.photo:
            return ""
        try:
            return item.photo.url
        except ValueError:
            return ""

    def is_active_value():
        if raw_data is not None:
            return 1 if str(raw_data.get("is_active", "")).lower() in ("on", "true", "1") else 0
        if item is not None:
            return 1 if item.is_active else 0
        return 1

    return [
        {
            "l": "عنوان آیتم *",
            "n": "title",
            "v": val("title"),
            "id": "the_title",
            "r": True,
            "c": "col-md-6",
            "b": "textBox.html",
        },
        {
            "l": "برچسب",
            "n": "badge",
            "v": val("badge"),
            "id": "the_badge",
            "r": None,
            "c": "col-md-3",
            "b": "textBox.html",
        },
        {
            "l": "فعال",
            "n": "is_active",
            "v": is_active_value(),
            "id": "is_active",
            "r": None,
            "c": "col-md-3",
            "b": "switch.html",
        },
        {
            "l": "تصویر",
            "n": "photo",
            "v": photo_url(),
            "id": "the_photo",
            "r": None,
            "c": "col-md-6",
            "b": "photo.html",
        },
    ]