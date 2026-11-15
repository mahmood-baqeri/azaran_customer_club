# applications/gift/forms.py

from django import forms
from django.urls import NoReverseMatch, reverse

from applications.core.forms import (
    make_input_item,
    make_select2_item,
    make_switch_item,
    make_image_item,
    pick_value,
    pick_bool,
)

from .models import Gift, GiftOrder


# ═══════════════════════════════════════════════════════════
# Action Forms (Django Forms مستقل — بدون تغییر)
# ═══════════════════════════════════════════════════════════
class OrderStatusForm(forms.Form):
    new_status = forms.ChoiceField(
        choices=GiftOrder.Status.choices,
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
# GIFT FORM — items برای قالب عمومی form.html
# ═══════════════════════════════════════════════════════════
def gift__form(gift=None, raw_data=None):
    """ساخت لیست items برای قالب عمومی form.html"""

    # ✅ برای کامپوننت گالری، Route حذف را از reverse() می‌سازیم
    # (جلوگیری از باگ مسیر نسبی)
    gallery_remove_route = None
    if gift is not None:
        try:
            gallery_remove_route = reverse("app_gift:delete_photo")
        except Exception:
            # اگر URL هنوز تعریف نشده، بدون قابلیت حذف ادامه بده
            gallery_remove_route = None

    return [
        # ─── عنوان ────────────────────────────────────────
        make_input_item(
            label="عنوان",
            name="title",
            input_id="the_title",
            value=pick_value(raw_data, gift, "title"),
            required=True,
            col_class="col-md-6",
        ),

        # ─── برای کاربر ──────────────────────────────────
        make_select2_item(
            label="برای",
            name="for_user",
            input_id="the_for_user",
            choices=[{"id": v, "label": l} for v, l in Gift.ForUser.choices],
            value=pick_value(raw_data, gift, "for_user", Gift.ForUser.SELLER),
            required=True,
            col_class="col-md-6",
        ),

        # ─── توضیحات ─────────────────────────────────────
        make_input_item(
            label="توضیحات",
            name="description",
            input_id="the_description",
            kind="textarea",
            value=pick_value(raw_data, gift, "description"),
            rows=4,
            col_class="col-md-12",
        ),

        # ─── ارزش / موجودی / فعال ────────────────────────
        make_input_item(
            label="ارزش آذر",
            name="azar_value",
            input_id="the_azar_value",
            kind="number",
            value=pick_value(raw_data, gift, "azar_value", 0),
            min=0,
            step=1,
            required=True,
            col_class="col-md-3",
        ),
        make_input_item(
            label="موجودی",
            name="stock",
            input_id="the_stock",
            kind="number",
            value=pick_value(raw_data, gift, "stock", 0),
            min=0,
            step=1,
            required=True,
            col_class="col-md-3",
        ),
        make_switch_item(
            label="فعال",
            name="is_active",
            input_id="is_active",
            value=pick_bool(raw_data, gift, "is_active"),
            col_class="col-md-3",
        ),

        # ─── تصویر شاخص ──────────────────────────────────
        make_image_item(
            label="تصویر",
            title="تصویر شاخص",
            name="photo",
            input_id="the_photo",
            existing=gift.photo if gift else None,
            col_class="col-md-3",
        ),

        # ─── گالری ───────────────────────────────────────
        make_image_item(
            label="گالری",
            title="گالری تصاویر",
            name="gallery",
            input_id="the_gallery",
            multiple=True,
            existing=gift.gallery if gift else None,
            allow_delete=bool(gift and gallery_remove_route),
            remove_route=gallery_remove_route,
            parent_id=gift.pk if gift else None,  
            col_class="col-md-12",
        ),
    ]