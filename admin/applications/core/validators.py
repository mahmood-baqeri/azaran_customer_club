# backend/apps/core/validators.py
from django.core.exceptions import ValidationError
from email_validator import validate_email, EmailNotValidError
import re
from dateutil.parser import parse


def validate_mobile(value):
    """اعتبارسنجی شماره موبایل ایران"""
    pattern = r'^09[0-9]{9}$'
    if not re.match(pattern, value):
        raise ValidationError('شماره موبایل باید با 09 شروع و 11 رقم باشد')

def is_valid_mobile(mobile):
    # mobile_regex = "^09(1[0-9]|3[1-9])-?[0-9]{3}-?[0-9]{4}$"
    mobile_regex = "^09\d{9}$"
    if (re.search(mobile_regex, mobile)):
        return True
    return None


def validate_iranian_national_code(value):
    """اعتبارسنجی کد ملی ایران"""
    if not value.isdigit() or len(value) != 10:
        raise ValidationError('کد ملی باید 10 رقم باشد')
    # الگوریتم اعتبارسنجی کد ملی
    check = int(value[9])
    s = sum(int(value[x]) * (10 - x) for x in range(9)) % 11
    if not (s < 2 and check == s or s >= 2 and check == 11 - s):
        raise ValidationError('کد ملی معتبر نیست')
    

def is_valid_iranian_national_code(code: str) -> bool:
    """اعتبارسنجی کد ملی ۱۰ رقمی ایران (checksum)"""
    if not code or not isinstance(code, str):
        return False
    code = code.strip()
    if len(code) != 10 or not code.isdigit():
        return False
    # کدهای تکراری مثل 0000000000 و 1111111111 معتبر نیستند
    if len(set(code)) == 1:
        return False
    check = int(code[9])
    s = sum(int(code[i]) * (10 - i) for i in range(9))
    r = s % 11
    return (r < 2 and check == r) or (r >= 2 and check == 11 - r)

def is_valid_nationalCode(input):
    if not re.search(r'^\d{10}$', input):
        return False
    check = int(input[9])
    s = sum(int(input[x]) * (10 - x) for x in range(9)) % 11
    return check == s if s < 2 else check + s == 11


def check_email(email):
    try:
        v = validate_email(email)
        return True
    except EmailNotValidError as e:
        print(str(e))
        return False

def checkEmail(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if (re.fullmatch(regex, email)):
        return True

    else:
        return False


def is_valid_date(string, fuzzy=False):
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False
