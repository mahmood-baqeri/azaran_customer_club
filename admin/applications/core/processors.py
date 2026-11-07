from time import time
import datetime
# from charity.models import Receipt
from django_dump_die.middleware import dd

from applications.role.models import Actions, Role
from applications.core.keyValue import Applications, settingPhoto
from applications.setting.models import Setting
from django.db.models import Q


def adminAccess(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"adminAccess": []}

    data = set()

    # 🧩 اگر کاربر مدیر معمولی
    if user.nature == "manager":
        role_ids = user.role_ids or []
        if not role_ids:
            return {"adminAccess": []}

        # 🔹 فقط با یک کوئری، همه‌ی action_ids مربوط به نقش‌ها رو جمع می‌کنیم
        roles = Role.objects.filter(pk__in=role_ids).values_list("action_ids", flat=True)
        all_action_ids = set()
        for ids in roles:
            if isinstance(ids, list):
                all_action_ids.update(ids)

        if not all_action_ids:
            return {"adminAccess": []}

        # 🔹 واکشی همه‌ی اکشن‌ها فقط یک‌بار و اضافه کردن مستقیم به set
        actions = Actions.objects.filter(pk__in=all_action_ids).values_list("action", flat=True)
        data.update(actions)

    return {"adminAccess": list(data)}



def checkActiveModule(request):
    data = []
    return {'checkActiveModule': data}




def initAppSetting(request):
    data = {}
    for item in Setting.objects.all():
        data[item.key] = str(item.value_file) if item.key in settingPhoto() else str(item.value_text)

    date = datetime.datetime.now()
    data['date'] = date.year
    return {'initAppSetting': data}


def sitSettings(request):
    data = {}
    for item in Setting.objects.all():
        data[item.key] = str(item.value_file) if item.key in settingPhoto() else str(item.value_text)

    date = datetime.datetime.now()
    data['date'] = date.year
    return {'sitSettings': data}



def adminNotifications(request):
    data = {
        'cash': 0,
        'order': 0,
        'skill': 0,
        'reserve': 0,
        'content': 0,
        'all': 0
    }
    return {'adminNotifications': data}


# Greater than:
# Person.objects.filter(age__gt=20)

# Greater than or equal to:
# Person.objects.filter(age__gte=20)

# Less than:
# Person.objects.filter(age__lt=20)

# Less than or equal to:
# Person.objects.filter(age__lte=20)
