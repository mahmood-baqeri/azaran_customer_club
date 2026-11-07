import json
import datetime

from jalali_date import date2jalali
from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter

from persiantools.jdatetime import JalaliDate

register = template.Library()


# ============================================================
# Helper Functions
# ============================================================

def parse_date(value):
    if isinstance(value, datetime.date):
        return value

    try:
        return datetime.datetime.strptime(str(value), "%Y-%m-%d").date()
    except Exception:
        return None


# ============================================================
# Inclusion Tags
# ============================================================

@register.inclusion_tag("components/tinymceComponnet.html")
def render_tinymce(name, value=None, id="textTinymce", height=300, custom_class=""):
    return {
        "n": name,
        "v": value,
        "id": id,
        "height": height,
        "custom_class": custom_class,
    }


# ============================================================
# Simple Tags
# ============================================================

@register.simple_tag
def paginationIndex(counter, page_size, page_number):
    if int(page_number) > 1:
        return int(counter) + ((int(page_number) - 1) * int(page_size))
    return counter


@register.simple_tag
def handleShareLink(request):
    return request.build_absolute_uri()


@register.simple_tag
def handleCenterPageAds(ads):
    mapping = {
        1: 12,
        2: 6,
        3: 4,
        4: 3,
        5: 2,
        6: 2,
    }
    return mapping.get(ads.count(), 0)


@register.simple_tag
def switchHandler(counter):
    return counter % 4 == 0


@register.simple_tag
def pageItemFadeInDuration(counter):
    return counter * 2


@register.simple_tag
def fnSumOfDeductions(net_payable, deductions):
    return "{:,.0f}".format(int(net_payable) + int(deductions))


@register.simple_tag
def currencyFormat(amount):
    if amount in (None, "", "0", 0):
        return "0"

    return "{:,.0f}".format(int(amount))


@register.simple_tag
def handelUrl(url_name, _id):
    return reverse(url_name, kwargs={"id": _id})


@register.simple_tag
def handelUrl2(url_name, user_id, record_id):
    return reverse(
        url_name,
        kwargs={
            "id": user_id,
            "recordID": record_id,
        },
    )


@register.simple_tag
def handelUrlChatPage(url_name, _type, slug):
    return reverse(
        url_name,
        kwargs={
            "type": _type,
            "slug": slug,
        },
    )


@register.simple_tag
def tableField(obj, field):
    return getattr(obj, field, "")


@register.simple_tag
def likedProduct(request, product_id):
    try:
        cookies = json.loads(
            request.COOKIES.get("userFavoriteProducts", "[]")
        )
        return product_id in cookies
    except Exception:
        return False


# ============================================================
# Json
# ============================================================

@register.filter
def parseJson(value):
    try:
        return json.loads(value)
    except Exception:
        return {}


@register.filter
def to_json(value):
    try:
        return mark_safe(json.dumps(value, ensure_ascii=False))
    except Exception:
        return "{}"
    
    
    
# ============================================================
# Date Filters
# ============================================================

@register.filter
def to_jalali(value, date_format="%Y/%m/%d"):
    """
    تبدیل تاریخ میلادی به شمسی
    """
    if not value:
        return ""

    date = parse_date(value)

    if date:
        try:
            return JalaliDate(date).strftime(date_format)
        except Exception:
            pass

    try:
        return JalaliDate(value).strftime(date_format)
    except Exception:
        return ""


@register.simple_tag
def gregorian_to_jalali(date):
    # اگر خالی یا '-' است → خروجی همان '-'
    if not date or date == '-' or date == 'None':
        return '-'

    # اگر datetime است
    if isinstance(date, datetime.date):
        year = date.year
        month = date.month
        day = date.day
    else:
        try:
            parts = str(date).split('-')
            if len(parts) != 3:
                return '-'

            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
        except:
            return '-'

    # تلاش برای تبدیل
    try:
        return JalaliDate(datetime.date(year, month, day)).strftime("%Y-%m-%d")
    except:
        return '-'


@register.simple_tag
def gregorian_to_jalali_2(date):
    if isinstance(date, datetime.date):
        year = int(date.year)
        month = int(date.month)
        day = int(date.day)
    else:
        _split = str(date).split('-')
        year = int(_split[0]) if date is not None else None
        month = int(_split[1]) if date is not None else None
        day = int(_split[2]) if date is not None else None
    try:
        return JalaliDate(datetime.date(year, month, day)).strftime("%d-%m-%Y")
    except:
        return ''

@register.simple_tag
def gregorian_to_jalali_month(date):
    if not date:
        return '-'

    if isinstance(date, datetime.date):
        year, month, day = date.year, date.month, date.day
    else:
        try:
            year, month, day = map(int, str(date).split('-'))
        except:
            return '-'

    try:
        j_date = date2jalali(datetime.date(year, month, day))
        month_names = [
            "فروردین", "اردیبهشت", "خرداد", "تیر",
            "مرداد", "شهریور", "مهر", "آبان",
            "آذر", "دی", "بهمن", "اسفند"
        ]
        j_month_name = month_names[j_date.month - 1]
        return f"{j_month_name} {j_date.year}"
    except Exception:
        return '-'

@register.simple_tag
def jalali_to_gregorian(jDate):
    date = jDate.split('-')
    if date[0] and date[1] and date[2]:
        return JalaliDate(int(date[0]), int(date[1]), int(date[2])).to_gregorian()


# ============================================================
# Form Filters
# ============================================================
@register.filter(name="get_field")
def get_field(form, field_name):
    """
    دریافت فیلد از فرم
    
    استفاده: {{ form|get_field:'title_fa' }}
    """
    if not form or not field_name:
        return ""
    
    try:
        # اگر فرم بایند شده باشد
        if hasattr(form, 'fields') and field_name in form.fields:
            # بازگرداندن فیلد با مقدار
            return form[field_name]
        return ""
    except Exception as e:
        # لاگ خطا در صورت نیاز
        print(f"Error in get_field: {e}")
        return ""


@register.filter
def get_field_value(form, field_name):
    """
    دریافت مقدار فیلد از فرم
    
    استفاده: {{ form|get_field_value:'title_fa' }}
    """
    if not form or not field_name:
        return ""
    
    try:
        if hasattr(form, 'initial') and field_name in form.initial:
            return form.initial.get(field_name, "")
        
        if hasattr(form, 'cleaned_data') and field_name in form.cleaned_data:
            return form.cleaned_data.get(field_name, "")
        
        if hasattr(form, 'data') and field_name in form.data:
            return form.data.get(field_name, "")
        
        return ""
    except Exception:
        return ""


@register.filter
def get_field_errors(form, field_name):
    """
    {{ form|get_field_errors:'title_fa' }}
    """
    if not form:
        return ""

    try:
        return form.errors.get(field_name)
    except Exception:
        return ""


@register.filter
def get_error(form, field_name):
    return get_field_errors(form, field_name)


@register.filter
def field_has_error(form, field_name):
    if not form:
        return False

    return field_name in form.errors


# ============================================================
# Dict / Object Filters
# ============================================================

@register.filter
def get_item(obj, key):
    """
    dictionary[key]
    """
    if obj is None:
        return ""

    if isinstance(obj, dict):
        return obj.get(key, "")

    return getattr(obj, key, "")


@register.filter
def get_attr(obj, attr):
    if obj is None:
        return ""

    return getattr(obj, attr, "")


# ============================================================
# Translation Filters
# ============================================================

@register.filter
def get_translated(obj, field_name):
    """
    {{ category|get_translated:'title' }}
    """

    if obj is None:
        return ""

    if hasattr(obj, "get_translated_field"):
        return obj.get_translated_field(field_name)

    return getattr(obj, field_name, "")


@register.filter
def get_translated_lang(args, lang_code):
    """
    {{ category|get_translated_lang:'title,fa' }}
    """

    try:
        obj, field_name = args
    except Exception:
        return ""

    if hasattr(obj, "get_translated_field"):
        return obj.get_translated_field(field_name, lang_code)

    return getattr(obj, field_name, "")


@register.simple_tag
def get_translated_field(obj, field_name, lang_code=None):
    if obj is None:
        return ""

    if hasattr(obj, "get_translated_field"):
        return obj.get_translated_field(field_name, lang_code)

    return getattr(obj, field_name, "")


@register.simple_tag
def get_category_title(category, lang_code=None):
    if category is None:
        return ""

    if hasattr(category, "get_translated_field"):
        return category.get_translated_field("title", lang_code)

    return getattr(category, "title", "")


@register.simple_tag
def get_category_description(category, lang_code=None):
    if category is None:
        return ""

    if hasattr(category, "get_translated_field"):
        return category.get_translated_field("description", lang_code)

    return getattr(category, "description", "")



# ============================================================
# String Filters
# ============================================================

@register.filter
@stringfilter
def persian_numbers(value):
    """
    تبدیل اعداد انگلیسی به فارسی
    """
    numbers = str.maketrans(
        "0123456789",
        "۰۱۲۳۴۵۶۷۸۹",
    )
    return value.translate(numbers)


@register.filter
def truncate_persian(text, length=100):
    """
    برش متن فارسی بدون نصف شدن کلمات
    """

    if not text:
        return ""

    text = str(text)

    if len(text) <= int(length):
        return text

    short = text[: int(length)]

    idx = short.rfind(" ")

    if idx > 0:
        short = short[:idx]

    return short + "..."


# ============================================================
# Misc
# ============================================================

@register.filter
def get_item_error(form, field_name):
    try:
        return form.errors.get(field_name)
    except Exception:
        return ""


@register.simple_tag
def empty_if_none(value, default=""):
    return value if value is not None else default


@register.filter
def yesno_fa(value):
    if value is True:
        return "بله"

    if value is False:
        return "خیر"

    return "-"


@register.filter
def bool_icon(value):
    if value:
        return mark_safe(
            '<i class="fas fa-check text-success"></i>'
        )

    return mark_safe(
        '<i class="fas fa-times text-danger"></i>'
    )
    


# ============================================================
# Number Formatting Filters
# ============================================================

@register.filter
def intcomma(value):
    """
    تبدیل اعداد به فرمت هزارگان با کاما
    
    استفاده: {{ price|intcomma }}
    
    مثال: 1500000 -> 1,500,000
    """
    if value is None or value == '':
        return '0'
    
    try:
        # اگر عدد بود
        if isinstance(value, (int, float)):
            return f"{value:,.0f}" if isinstance(value, int) else f"{value:,.2f}"
        
        # اگر رشته بود
        value = str(value).strip()
        if not value:
            return '0'
        
        # تبدیل به عدد
        num = float(value)
        return f"{num:,.0f}" if num.is_integer() else f"{num:,.2f}"
    
    except (ValueError, TypeError):
        return str(value)


@register.filter
def intcomma_fa(value):
    """
    تبدیل اعداد به فرمت هزارگان با کاما و اعداد فارسی
    
    استفاده: {{ price|intcomma_fa }}
    
    مثال: 1500000 -> ۱,۵۰۰,۰۰۰
    """
    if value is None or value == '':
        return '۰'
    
    try:
        # اگر عدد بود
        if isinstance(value, (int, float)):
            result = f"{value:,.0f}" if isinstance(value, int) else f"{value:,.2f}"
        else:
            # اگر رشته بود
            value = str(value).strip()
            if not value:
                return '۰'
            num = float(value)
            result = f"{num:,.0f}" if num.is_integer() else f"{num:,.2f}"
        
        # تبدیل به فارسی
        persian_map = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
        return result.translate(persian_map)
    
    except (ValueError, TypeError):
        return str(value)


@register.filter
def currency(value, currency_symbol='تومان'):
    """
    نمایش قیمت به صورت فرمت شده با واحد پولی
    
    استفاده: {{ price|currency }}
    {{ price|currency:'ریال' }}
    
    مثال: 1500000 -> 1,500,000 تومان
    """
    if value is None or value == '':
        return f'۰ {currency_symbol}'
    
    try:
        num = float(value)
        formatted = f"{num:,.0f}" if num.is_integer() else f"{num:,.2f}"
        return f"{formatted} {currency_symbol}"
    
    except (ValueError, TypeError):
        return f"{value} {currency_symbol}"


@register.filter
def currency_fa(value, currency_symbol='تومان'):
    """
    نمایش قیمت به صورت فرمت شده با اعداد فارسی و واحد پولی
    
    استفاده: {{ price|currency_fa }}
    {{ price|currency_fa:'ریال' }}
    
    مثال: 1500000 -> ۱,۵۰۰,۰۰۰ تومان
    """
    if value is None or value == '':
        return f'۰ {currency_symbol}'
    
    try:
        num = float(value)
        formatted = f"{num:,.0f}" if num.is_integer() else f"{num:,.2f}"
        
        # تبدیل به فارسی
        persian_map = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
        formatted_fa = formatted.translate(persian_map)
        
        return f"{formatted_fa} {currency_symbol}"
    
    except (ValueError, TypeError):
        return f"{value} {currency_symbol}"