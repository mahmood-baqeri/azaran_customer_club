from django import forms
from django.utils.translation import gettext_lazy as _

from applications.page.models import Category, Page, PageContentItem


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        default_attrs = {"multiple": True}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class PageForm(forms.ModelForm):
    """فرم ایجاد/ویرایش صفحه — منطبق با مدل ساده‌شده"""

    gallery_images = forms.FileField(
        label=_("آپلود تصاویر گالری"),
        required=False,
        widget=MultipleFileInput(attrs={"class": "form-control", "accept": "image/*"}),
    )

    class Meta:
        model = Page
        fields = [
            "category", "type",
            "title", "summer", "text",
            "photo", "gallery",
            "is_active",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "maxlength": 120}),
            "summer": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "text": forms.Textarea(attrs={"class": "form-control online-editor", "rows": 10}),
            "photo": forms.FileInput(attrs={"class": "form-control"}),
            "gallery": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # category
        self.fields["category"].required = False
        self.fields["category"].queryset = Category.objects.filter(is_active=True)
        self.fields["category"].widget = forms.Select(attrs={"class": "form-control select2"})

        # type
        self.fields["type"].widget = forms.Select(attrs={"class": "form-control"})
        self.fields["type"].choices = Page.PageType.choices

        # is_active
        self.fields["is_active"].required = False
        self.fields["is_active"].widget = forms.CheckboxInput(
            attrs={"class": "form-check-input", "role": "switch"}
        )

        # gallery — فقط برای آپلود مستقیم نیست؛ فیلد مخفی
        self.fields["gallery"].required = False

        # اگر رکورد موجود است، گالری را مقدار اولیه بده
        if self.instance and self.instance.pk and isinstance(self.instance.gallery, list):
            import json
            self.initial["gallery"] = json.dumps(self.instance.gallery, ensure_ascii=False)

    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()
        if not title:
            raise forms.ValidationError(_("عنوان الزامی است"))
        return title

    def clean(self):
        cleaned_data = super().clean()
        is_active = cleaned_data.get("is_active", False)

        # حداقل یکی از متن کوتاه یا متن اصلی باید باشد
        if is_active and not (cleaned_data.get("summer") or cleaned_data.get("text")):
            self.add_error("summer", _("صفحه فعال باید حداقل یک متن کوتاه یا متن اصلی داشته باشد"))

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # فیلد gallery از فرم مخفی — کاربر ممکن است JSON داده باشد
        gallery_raw = self.cleaned_data.get("gallery")
        if isinstance(gallery_raw, str) and gallery_raw.strip():
            import json
            try:
                instance.gallery = json.loads(gallery_raw)
            except Exception:
                instance.gallery = []
        elif isinstance(gallery_raw, list):
            instance.gallery = gallery_raw

        if commit:
            instance.save()
        return instance


class PageFilterForm(forms.Form):
    """فرم فیلتر لیست صفحات"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("جستجو در عنوان، متن...")}
        ),
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label=_("همه دسته‌بندی‌ها"),
        widget=forms.Select(attrs={"class": "form-control select2"}),
    )

    type = forms.ChoiceField(
        choices=[("", _("همه"))] + list(Page.PageType.choices),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    is_active = forms.ChoiceField(
        choices=[("", _("همه")), ("True", _("فعال")), ("False", _("غیرفعال"))],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class PageContentItemForm(forms.ModelForm):
    """فرم مدیریت محتوای صفحه (Step/FAQ)"""

    class Meta:
        model = PageContentItem
        fields = ["kind", "title", "body", "order", "extra"]
        widgets = {
            "kind": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control", "maxlength": 255}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "order": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "extra": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": _('{"icon": "fa-icon", "link": "https://..."}'),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["extra"].required = False
        self.fields["title"].required = True
        self.fields["body"].required = False