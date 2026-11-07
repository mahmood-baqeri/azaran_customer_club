from django.utils.translation import gettext_lazy as _

from django.db import models


class QuestionTypes(models.TextChoices):
    MultipleChoice = "multipleChoice", _('MultipleChoice')
    Height = "height", _('Height')
    Weight = "weight", _('Weight')


class ProgramTypes(models.TextChoices):
    Predefined = "Predefined", _('Predefined') # برنامه از پیش تعریف شده
    Personal = "Personal", _('Personal')  # برنامه شخصی


def lanquages():
    return (
        ('en', 'English'),
        ('fa', 'Persian'),
        ('fr', 'French'),
        ('tr', 'Turkish'),
        ('ar', 'Arabic'),
    )


def LoginType():
    return (
        (1, 'Login With Pass'),
        (2, 'Login With SMS'),
    )


def userMetaRelated():
    return (
        (1, 'AnswerQuestions'),
        (2, ''),
    )


def chatItemsOwner():
    return (
        ('SideA', 'SideA'),
        ('SideB', 'SideB'),
    )


def activeStatus():
    return (
        (1, _('Active')),
        (0, _('Deactivate'))
    )


def Pages():
    return (
        ('Home', 'Home'),
        ('AboutUs', 'About Us'),
        ('ContactUs', 'Contact Us'),
        ('Faq', 'Faq'),
        ('Pricing', 'Pricing'),
        ('Rule', 'Rule'),
        ('Models', 'Models'),
        ('Ticket', 'Ticket'),
        ('Download', 'Download App'),
        ('Subscription', 'Subscription'),
    )


def Gender():
    return (
        (1, _('Male')),
        (0, _('Female'))
    )


def FileType():
    return (
        (0, 'photo'),
        (1, 'video'),
        (2, 'audio'),
        (3, 'pdf'),
    )


def AppCharacter():
    return (
        ('Coach', _('Coach')),
        ('Gym', _('Gym')),
        ('Spa', _('Spa')),
    )


def weekDate():
    return (
        ('Saturday', _('Saturday')),
        ('Sunday', _('Sunday')),
        ('Monday', _('Monday')),
        ('Tuesday', _('Tuesday')),
        ('Wednesday', _('Wednesday')),
        ('Thursday', _('Thursday')),
        ('Friday', _('Friday')),
    )


def publishStatus():
    return (
        (0, _('Save')),
        (1, _('Publish')),
        (2, _('Confirm'))
    )


def paymentStatus():
    return (
        (0, _('Awaiting Payment')),
        (1, _('Paid')),
    )


def YesNo():
    return (
        (1, _('Yes')),
        (0, _('No'))
    )


def Currency():
    return (
        (1, _('Lira')),
        (2, _('Dollar')),
        (3, _('Rial')),
        (4, _('Pound')),
        (5, _('Euro')),
    )


def CurrencyFlag():
    return (
        ('Lira', _('₺')),
        ('Dollar', _('$')),
        ('Rial', _('IRR')),
        ('Pound', _('£')),
        ('Euro', _('€')),
    )

# ثابت‌های مربوط به Currency
CURRENCY_FLAG_MAP = {
    1: '₺',    # Lira
    2: '$',    # Dollar
    3: 'IRR',  # Rial
    4: '£',    # Pound
    5: '€',    # Euro
}


def OffType():
    return (
        (0, _('None')),
        (1, _('Percent')),
        (2, _('Amount')),
    )


def adPosition():
    return (
        (0, _('Mina Page') + ' ' + _('Slider') + ' ' + _('Side')),
        (1, _('Footer') + ' ' + _('Top')),
        (2, _('News') + ' ' + _('Side')),
        (3, _('Shop') + ' ' + _('Side')),
        (4, _('Coach') + ' ' + _('Side')),
        (5, _('Club') + ' ' + _('Side')),
    )


def Levels():
    return (
        (1, _('Beginner')),
        (2, _('Intermediate')),
        (3, _('Advanced')),
        (4, _('Expert')),
        (5, _('Master')),
    )


def elementType():
    return (
        ('1', 'Text'),
        ('2', 'Long Text'),
        ('3', 'Photo'),
    )


def appSettings():
    return (
        ('Logo', 'لوگو'),
        ('FavIcon', 'فاوآیکن'),

        ('Address', 'آدرس'),
        ('Phone', 'تلفن'),
        

        ('Telegram', 'تلگرام'),
        ('Instagram', 'اینستاگرام'),
        ('Facebook', 'فیسبوک'),
        ('Twitter', 'ایکس'),
        ('Linkedin', 'لینکدین'),
        ('Email', 'ایمیل'),
    )


def settingPhoto():
    return ['Logo', 'FavIcon', 'Hero_Photo']


def settingBoolean():
    return ['ActiveContent']


def settingLong():
    return ['AboutUs', 'FooterText']


def settingNumbers():
    return ['Phone', 'ActiveUsers', 'CompanyTools', 'CustomerTools']


def settingTextareas():
    return ['Address', 'Location', 'CopyRight', "Slogan_Long", "MetaTitle", "MetaDescription", "MetaKeywords"]


def LogUserType():
    return (
        (0, 'User'),
        (1, 'Admin'),
    )


def Applications():
    return (
        ('Admin', 'Admin'),
        ('User', 'User'),
        ('Backend', 'Backend'),
        ('Role', 'Role'),
        ('Log', 'Log'),
        ('Setting', 'Setting'),
        ('Category', 'Category'),
        ('News', 'News'),
        ('AdminPanel', 'AdminPanel'),
        ('Page', 'Page'),
        ('Service', 'Service'),
    )


def searchInApplication(key):
    applications = Applications()
    for app in applications:
        if app[0] == key:
            return app[1]
    return None


def Verify():
    return (
        (0, 'Reject'),
        (1, 'Verify'),
    )
