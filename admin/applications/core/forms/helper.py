# Path: applications/core/forms/helper.py

# applications/core/forms/helper.py

import json
from datetime import date, datetime

from django.conf import settings



# applications/core/forms/helper.py — این توابع را اضافه کن
# (بعد از pick_multi و pick_switch_group)

def _read_multi_from_raw(raw_data, name, prefix=None):
    """خواندن مقادیر چندتایی از POST/QueryDict یا dict عادی."""
    if hasattr(raw_data, "getlist"):
        if prefix is None:
            return raw_data.getlist(name) or []
        return [k[len(prefix):] for k in raw_data if k.startswith(prefix)]

    # dict عادی
    if prefix is not None:
        return [k[len(prefix):] for k in raw_data if k.startswith(prefix)]
    val = raw_data.get(name)
    if val is None:
        return []
    if isinstance(val, (list, tuple, set)):
        return [str(v) for v in val]
    return [str(val)]


def _read_multi_from_model(model, model_attr):
    """خواندن مقادیر چندتایی از مدل (QuerySet / Manager / list / JSON)."""
    if model is None:
        return []
    val = getattr(model, model_attr, None)
    if val is None:
        return []
    if hasattr(val, "values_list"):
        return list(val.values_list("pk", flat=True))
    if hasattr(val, "all"):
        return list(val.all().values_list("pk", flat=True))
    try:
        return list(val)
    except TypeError:
        return [val]


def pick_multi_or_model(raw_data, name, model, model_attr):
    """
    برای Select2 multiple:
      - POST موجود → getlist(name) — حتی اگر خالی (احترام به تصمیم کاربر)
      - وگرنه → model.model_attr
    """
    if raw_data is not None:
        return _read_multi_from_raw(raw_data, name)
    return _read_multi_from_model(model, model_attr)


def pick_switch_group_or_model(raw_data, name, model, model_attr):
    """
    برای سوئیچ گروهی (name#id):
      - POST موجود → استخراج idها از کلیدهای name#...
      - وگرنه → model.model_attr
    """
    if raw_data is not None:
        return _read_multi_from_raw(raw_data, name, prefix=f"{name}#")
    return _read_multi_from_model(model, model_attr)


def make_divider_item():
    """جداکننده افقی بین بخش‌های فرم."""
    return {'b': 'hr.html'}


def pick_value_any(raw_data, model, model_field, *raw_fields, default=''):
    """
    مثل pick_value، اما در raw_data چند نام را امتحان می‌کند.
    مثال: pick_value_any(raw_data, profile, "province_id", "province")
    """
    if raw_data is not None:
        for f in (model_field, *raw_fields):
            if f in raw_data:
                return raw_data.get(f)
    if model is not None:
        return getattr(model, model_field, default)
    return default


def coerce_datetime(value):
    """هر ورودی رایج → datetime | None."""
    if value in (None, '', 'None'):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if isinstance(value, str):
        for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%d %H:%M', '%Y-%m-%d'):
            try:
                return datetime.strptime(value.strip(), fmt)
            except ValueError:
                continue
    return None


def serialize_json(value, indent=2):
    """dict/list → JSON string (برای Textarea). رشته را دست‌نخورده."""
    if value is None or value == '':
        return ''
    if isinstance(value, str):
        return value
    return json.dumps(value, indent=indent, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════
# Type Coercion
# ═══════════════════════════════════════════════════════════
def coerce_date(value):
    """هر ورودی رایج → date | None."""
    if value in (None, '', 'None'):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%Y-%m-%d %H:%M:%S'):
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                continue
    return None


def to_bool(value):
    """هر ورودی رایج → True/False."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in ('1', 'on', 'true', 'yes', 'y', 't')
    return False


def to_int(value):
    """هر ورودی رایج → int | None."""
    if value in (None, '', 'None'):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def media_url(path_or_url):
    """مسیر نسبی → URL کامل (با MEDIA_URL). مسیر مطلق دست‌نخورده."""
    if not path_or_url:
        return ''
    if str(path_or_url).startswith(('http://', 'https://', '//', '/')):
        return path_or_url
    return f'{settings.MEDIA_URL}{path_or_url}'


# ═══════════════════════════════════════════════════════════
# Normalizers (ورودی make_*_item را استاندارد می‌کنند)
# ═══════════════════════════════════════════════════════════
def normalize_choices(choices):
    """list[dict|tuple|model|str] → list[{'id': str, 'label': str}]."""
    out = []
    for c in (choices or []):
        if isinstance(c, dict):
            cid = c.get('id')
            label = c.get('label') or c.get('name') or str(cid)
        elif isinstance(c, (list, tuple)) and len(c) == 2:
            cid, label = c
        elif hasattr(c, 'pk'):
            cid, label = c.pk, str(c)
        else:
            cid, label = c, str(c)
        out.append({'id': str(cid), 'label': label})
    return out


def normalize_selection(value, multiple):
    """مقدار(های) انتخاب‌شده → set از رشته (multiple) یا رشته (single)."""
    if value in (None, ''):
        return set() if multiple else None
    if hasattr(value, 'values_list'):
        value = list(value.values_list('pk', flat=True))
    if multiple:
        if isinstance(value, (list, tuple, set)):
            return {str(v) for v in value if v not in (None, '')}
        return {str(value)}
    return str(value)


def _normalize_single_file(item, index):
    """یک آیتم فایل → dict استاندارد یا None (رد شود)."""
    # FieldFile مستقیم
    if hasattr(item, 'url'):
        try:
            url = item.url
        except (ValueError, AttributeError):
            return None
        return {
            'name':  (getattr(item, 'name', '') or '').rsplit('/', 1)[-1],
            'url':   url,
            'id':    getattr(item, 'pk', None),
            'index': index,
        }

    # دیکشنری
    if isinstance(item, dict):
        url = media_url(item.get('url') or item.get('path') or '')
        if not url:
            return None
        return {
            'name':  item.get('name') or url.rsplit('/', 1)[-1],
            'url':   url,
            'id':    item.get('id'),
            'index': index,
        }

    # رشته
    if isinstance(item, str):
        url = media_url(item)
        return {
            'name':  item.rsplit('/', 1)[-1],
            'url':   url,
            'id':    None,
            'index': index,
        }

    # مدل (مثل PostImage) — جستجوی فیلد فایل رایج
    for fname in ('image', 'file', 'photo', 'attachment', 'document'):
        field = getattr(item, fname, None)
        if field and hasattr(field, 'url'):
            try:
                url = field.url
            except (ValueError, AttributeError):
                continue
            return {
                'name':  (field.name or '').rsplit('/', 1)[-1],
                'url':   url,
                'id':    getattr(item, 'pk', None),
                'index': index,
            }

    return None


def normalize_files(source):
    """
    هر شکلی از ورودی → list[{'name','url','id','index'}].
    ورودی‌های مجاز:
      - None
      - FieldFile منفرد
      - Manager/QuerySet (روی مدل‌هایی که فیلد image/file/photo/... دارند)
      - list از str/dict/FieldFile/مدل
    """
    if not source:
        return []

    # FieldFile منفرد (نه Manager، نه QuerySet)
    if (hasattr(source, 'url') and hasattr(source, 'name')
            and not hasattr(source, 'all')):
        result = _normalize_single_file(source, 0)
        return [result] if result else []

    # Manager / QuerySet
    if hasattr(source, 'all') and callable(source.all):
        source = list(source.all())

    if not isinstance(source, (list, tuple, set)):
        source = [source]

    out = []
    for i, item in enumerate(source):
        result = _normalize_single_file(item, i)
        if result:
            out.append(result)
    return out


# ═══════════════════════════════════════════════════════════
# Pickers (POST → model → default)
# ═══════════════════════════════════════════════════════════
def pick_value(raw_data, model, field, default=''):
    """فیلد متنی: اگر در POST کلید باشد (حتی خالی) → POST، وگرنه مدل، وگرنه default."""
    if raw_data is not None and field in raw_data:
        return raw_data.get(field)
    if model is not None:
        return getattr(model, field, default)
    return default


def pick_bool(raw_data, model, field, default=False):
    """سوئیچ تک: اگر فرم submit شده (raw_data موجود) → وجود کلید = True."""
    if raw_data is not None:
        return field in raw_data
    if model is not None:
        return getattr(model, field, default)
    return default


def pick_multi(raw_data, name):
    """Select2 multiple: لیست رشته‌ها از POST."""
    if raw_data is None:
        return []
    return raw_data.getlist(name) or []


def pick_switch_group(raw_data, name):
    """سوئیچ گروهی (name#id): لیست idها از POST."""
    if raw_data is None:
        return []
    prefix = f'{name}#'
    return [k[len(prefix):] for k in raw_data if k.startswith(prefix)]


def pick_file(request, name):
    """فایل آپلودشده‌ی تک یا None."""
    return request.FILES.get(name)


def pick_files(request, name):
    """فایل‌های آپلودشده‌ی چندتایی."""
    return request.FILES.getlist(name) or []


def require_fields(raw_data, *fields):
    """لیست فیلدهای خالی (بعد از strip)."""
    return [f for f in fields if not (raw_data.get(f) or '').strip()]