# applications/gift/forms.py

from django import forms

from .models import Gift, GiftOrder


# ═══════════════════════════════════════════════════════════
# Action Forms (داخل صفحه‌ی جزئیات سفارش)
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

    def val(field, default=""):
        if raw_data is not None:
            return raw_data.get(field, default)
        if gift is not None:
            return getattr(gift, field, default)
        return default

    def photo_url():
        """✅ URL رشته برمی‌گرداند (نه ImageFieldFile)"""
        if not gift or not gift.photo:
            return ""
        try:
            return gift.photo.url
        except ValueError:
            return ""

    def is_active_value():
        """✅ raw_data را هم در نظر می‌گیرد"""
        if raw_data is not None:
            v = str(raw_data.get("is_active", "")).lower()
            return 1 if v in ("on", "true", "1") else 0
        if gift is not None:
            return 1 if gift.is_active else 0
        return 0

    def gallery_photos():
        """گالری از DB (منبع حقیقت — AJAX delete فوری ذخیره می‌شود)"""
        if gift is not None:
            return list(gift.gallery or [])
        return []

    return [
        {
            'l': "عنوان *",
            'n': 'title',
            'v': val("title"),
            'id': 'the_title',
            'r': True,
            'c': 'col-md-6',
            'b': 'textBox.html'
        }, {
            'l': "برای *",
            'n': 'for_user',
            'v': val("for_user", Gift.ForUser.SELLER),
            'id': 'the_for_user',
            'r': True,
            'c': 'col-md-6',
            'data': [{"id": v, "label": l} for v, l in Gift.ForUser.choices],
            'b': 'select2Single.html',
        }, {
            'l': "توضیحات",
            'n': 'description',
            'v': val("description"),
            'id': 'the_description',
            'r': None,
            'c': 'col-md-12',
            'b': 'textarea.html'
        }, {
            'l': 'ارزش آذر *',
            'n': 'azar_value',
            'v': val("azar_value", 0),
            'id': 'the_azar_value',
            'r': True,
            'c': 'col-md-3',
            'b': 'number.html'
        }, {
            'l': 'موجودی *',
            'n': 'stock',
            'v': val("stock", 0),
            'id': 'the_stock',
            'r': True,
            'c': 'col-md-3',
            'b': 'number.html'
        }, {
            'l': 'فعال',
            'n': 'is_active',
            'v': is_active_value(),
            'id': 'is_active',
            'r': None,
            'c': 'col-md-3',
            'b': 'switch.html'
        }, {
            'l': 'تصویر',
            'n': 'photo',
            'v': photo_url(),
            'id': 'the_photo',
            'r': None,
            'c': 'col-md-3',
            'b': 'photo.html'
        }, {
            'l': "گالری",
            'n': 'gallery',
            'photos': gallery_photos(),
            'theItem': gift if gift else '',
            'id': 'the_gallery',
            'r': None,
            'removeRoute': "gift/api/deletePhoto",
            'c': 'col-md-12',
            'b': 'photoMulti.html'
        }
    ]