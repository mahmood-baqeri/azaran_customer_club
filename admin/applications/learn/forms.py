
from applications.role.models import Role


def backend__userForm(item):
    is_active = 0
    if item:
        if item.is_active:
            is_active = 1

    data = [
        {
            'l': 'نام',
            'n': 'first_name',
            'v': item.first_name if item else '',
            'id': 'thefirst_name',
            'r': 1,
            'c': 'col-md-3',
            'b': 'textBox.html'
        }, {
            'l': 'نام خانوادگی',
            'n': 'last_name',
            'v': item.last_name if item else '',
            'id': 'thelast_name',
            'r': 1,
            'c': 'col-md-3',
            'b': 'textBox.html'
        }, {
            'l': 'تلفن همراه',
            'n': 'mobile',
            'v': item.mobile if item else '',
            'id': 'mobile',
            'r': 1,
            'c': 'col-md-3',
            'b': 'number.html'
        }, {
            'l': 'رمز عبور جدید',
            'n': 'password',
            'v': '',
            'id': 'thePassEl2',
            'r': None,
            'c': 'col-md-3',
            'b': 'textBox.html'
        },

              {'b': 'hr.html'},
        {
            'l': 'فعال',
            'n': 'active',
            'v': is_active,
            'id': 'theActiveEl',
            'r': None,
            'c': 'col-md-2',
            'b': 'switch.html'
        },
    ]
    return data


def backend__adminForm(item):
    is_active = 0
    if item:
        if item.is_active:
            is_active = 1

    select2 = []
    for role in Role.objects.all():
        select2.append({'label': role.title, 'id': role.id})

    data = [
        {
            'l': 'نام',
            'n': 'first_name',
            'v': item.first_name if item else '',
            'id': 'first_name',
            'r': 1,
            'c': 'col-md-3',
            'b': 'textBox.html'
        },
        {
            'l': 'نام خانوادگی',
            'n': 'last_name',
            'v': item.last_name if item else '',
            'id': 'last_name',
            'r': 1,
            'c': 'col-md-3',
            'b': 'textBox.html'
        }, {
            'l': 'تلفن همراه',
            'n': 'mobile',
            'v': item.mobile if item else '',
            'id': 'mobile',
            'r': 1,
            'c': 'col-md-3',
            'b': 'number.html'
        },
        {
            'l': 'تصویر شخصی',
            'n': 'photo',
            'v': item.photo if item else '',
            'id': 'photo',
            'r': None,
            'c': 'col-md-3',
            'b': 'photo.html'
        },
       
        {'b': 'hr.html'},

        {
            'l': 'سطح دسترسی',
            'n': 'roles',
            'v': item.role_ids if item else [],
            'id': 'theRolesElement',
            'r': 1,
            'c': 'col-md-3',
            'data': select2,
            'b': 'select2Multi.html'
        },
        {
            'l': 'فعال',
            'n': 'active',
            'v': is_active,
            'id': 'active',
            'r': None,
            'c': 'col-md-3',
            'b': 'switch.html'
        },

        {'b': 'hr.html'},

    ]
    return data


def backend__profileForm(item):
    data = [
        {'l': 'نام', 'n': 'first_name', 'v': item.first_name if item else '', 'id': 1, 'r': 1, 'c': 'col-md-4',
         'b': 'textBox.html'},
        {'l': 'نام خانوادگی', 'n': 'last_name', 'v': item.last_name if item else '', 'id': 1, 'r': 1, 'c': 'col-md-4',
         'b': 'textBox.html'},
        {'l': 'تلفن همراه', 'n': 'mobile', 'v': item.mobile if item else '', 'id': 1, 'r': 1, 'c': 'col-md-4',
         'b': 'number.html'},
        {'l': 'آدرس', 'n': 'address', 'v': item.address if item else '', 'id': 1, 'r': None, 'c': 'col-md-4',
         'b': 'textBox.html'},
        {'l': 'تصویر شخصی', 'n': 'photo', 'v': item.photo if item else '', 'id': 1, 'r': None, 'c': 'col-md-4',
         'b': 'photo.html'},
    ]
    return data


def backend__changePass():
    return [
        {'l': 'رمز عبور فعلی', 'n': 'oldPassword', 'v': '', 'id': 'thePassEl1', 'r': 1, 'c': 'col-6 offset-r-3', 'b': 'password.html'},
        {'l': 'رمز عبور جدید', 'n': 'newPassword', 'v': '', 'id': 'thePassEl2', 'r': 1, 'c': 'col-6 offset-r-3', 'b': 'password.html'},
        {'l': 'تکرار رمز عبور', 'n': 'rePassword', 'v': '', 'id': 'thePassEl3', 'r': 1, 'c': 'col-6 offset-r-3', 'b': 'password.html'},
    ]
