from django import forms
from django.utils.translation import gettext_lazy as _

from applications.category.models import Category


class CategoryForm(forms.ModelForm):
    """فرم ایجاد/ویرایش دسته‌بندی"""

    class Meta:
        model = Category
        fields = ["title", "description", "parent", "is_active"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "maxlength": 120, "placeholder": _("عنوان دسته‌بندی")}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": _("توضیحات اختیاری")}
            ),
            "parent": forms.Select(attrs={"class": "form-control select2"}),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input", "role": "switch"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parent"].required = False
        self.fields["parent"].queryset = Category.objects.filter(is_active=True)
        self.fields["is_active"].required = False

        # در ویرایش، خودش و فرزندانش نباید در والد قابل انتخاب باشند
        if self.instance and self.instance.pk:
            descendants = self._get_descendants(self.instance)
            excluded_ids = [self.instance.pk] + [d.pk for d in descendants]
            self.fields["parent"].queryset = Category.objects.filter(
                is_active=True
            ).exclude(pk__in=excluded_ids)

    def _get_descendants(self, category):
        """همه‌ی فرزندان (بازگشتی) را برمی‌گرداند."""
        descendants = []
        for child in category.children.all():
            descendants.append(child)
            descendants.extend(self._get_descendants(child))
        return descendants

    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()
        if not title:
            raise forms.ValidationError(_("عنوان الزامی است"))
        # چک یکتایی در سطح هم‌سطح (اختیاری)
        qs = Category.objects.filter(title=title)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_("دسته‌بندی با این عنوان قبلاً وجود دارد"))
        return title

    def clean(self):
        cleaned = super().clean()
        parent = cleaned.get("parent")
        if parent and self.instance and self.instance.pk:
            # چک حلقه
            node = parent
            while node is not None:
                if node.pk == self.instance.pk:
                    self.add_error("parent", _("نمی‌توانید یک دسته‌بندی را والد خودش یا فرزندانش قرار دهید"))
                    break
                node = node.parent
        return cleaned


class CategoryFilterForm(forms.Form):
    """فرم فیلتر لیست دسته‌بندی"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("جستجو در عنوان...")}
        ),
    )
    is_active = forms.ChoiceField(
        choices=[("", _("همه")), ("True", _("فعال")), ("False", _("غیرفعال"))],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    parent = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label=_("همه والدها"),
        widget=forms.Select(attrs={"class": "form-control select2"}),
    )