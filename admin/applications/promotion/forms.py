# Path: applications/promotion/forms.py

# applications/promotion/forms.py

from django import forms

# ← یک import، همه‌ی helperها و make_*_itemها
from applications.core.forms import (
    make_input_item,
    make_switch_item,
    make_image_item,
    pick_value,
    pick_bool,
)

from .models import Promotion, PromotionItem, PromotionOrder


# ═══════════════════════════════════════════════════════════
# Action Forms (Django Forms مستقل — بدون تغییر)
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

    return [
        make_input_item(
            label="عنوان پک",
            name="title",
            input_id="the_title",
            value=pick_value(raw_data, promotion, "title"),
            required=True,
            col_class="col-md-9",
        ),
        make_switch_item(
            label="فعال",
            name="is_active",
            input_id="is_active",
            value=pick_bool(raw_data, promotion, "is_active", default=True),
            col_class="col-md-3",
        ),
    ]


# ═══════════════════════════════════════════════════════════
# PROMOTION ITEM FORM
# ═══════════════════════════════════════════════════════════
def promotion_item__form(item=None, raw_data=None):
    """items برای قالب عمومی form.html — آیتم داخل پک"""

    return [
        make_input_item(
            label="عنوان آیتم",
            name="title",
            input_id="the_title",
            value=pick_value(raw_data, item, "title"),
            required=True,
            col_class="col-md-6",
        ),
        make_input_item(
            label="برچسب",
            name="badge",
            input_id="the_badge",
            value=pick_value(raw_data, item, "badge"),
            col_class="col-md-3",
        ),
        make_switch_item(
            label="فعال",
            name="is_active",
            input_id="is_active",
            value=pick_bool(raw_data, item, "is_active", default=True),
            col_class="col-md-3",
        ),
        make_image_item(
            label="تصویر",
            title="تصویر آیتم",
            name="photo",
            input_id="the_photo",
            existing=item.photo if item else None,
            col_class="col-md-6",
        ),
    ]