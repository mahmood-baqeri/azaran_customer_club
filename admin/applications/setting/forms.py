import json
from applications.core.keyValue import appSettings, adPosition, Pages, settingPhoto, settingNumbers, settingBoolean, settingLong, settingTextareas


def setting__setting__form(item=None):
    select2 = []
    for ac in appSettings():
        select2.append({'label': ac[1], 'id': ac[0]})

    return [
        {
            'l': 'گزینه',
            'n': 'key',
            'v': item.key if item else '',
            'id': 'settingSelectedTheItem',
            'r': None,
            'data': select2,
            'c': 'col-md-4',
            'b': 'select2Single.html',
        }, {
            'l': "تصویر",
            'n': 'photo',
            'v': item.value_file if item else '',
            'id': 'thePhotoElement',
            'r': None,
            'c': 'col-md-4 theSettingItemRoot d-none',
            'b': 'photo.html'
        }, {
            'l': "عدد",
            'n': '',
            'v': item.value_text if item else '',
            'id': 'theNumberElement',
            'r': None,
            'c': 'col-md-4 theSettingItemRoot d-none',
            'b': 'number.html'
        }, {
            'l': "متن",
            'n': '',
            'v': item.value_text if item else '',
            'id': 'theTextElement',
            'r': None,
            'c': 'col-md-8 theSettingItemRoot d-none',
            'b': 'textBox.html'
        }, {
            'l': "متن" + " " + "کوتاه",
            'n': '',
            'v': item.value_text if item else '',
            'id': 'theTextAreaElement',
            'r': None,
            'c': 'col-md-12 theSettingItemRoot d-none',
            'b': 'textarea.html'
        },
        {
            'l': "متن" + " " + "طولانی",
            'n': '',
            'v': item.value_text if item else '',
            'id': 'theCkEditorElement',
            'r': None,
            'c': 'col-md-12 theSettingItemRoot d-none',
            'b': 'tinymceUseForSetting.html'
        },
        {
            'l': "وضعیت فعال",
            'n': '',
            'v': item.value_text if item else '',
            'id': 'theBooleanElement',
            'r': None,
            'c': 'col-md-4 theSettingItemRoot d-none',
            'b': 'switch.html'
        },
        {
            'b': 'manageSetting.html',
            'settingGroups': {
                'thePhotoElement': settingPhoto(),
                'theNumberElement': settingNumbers(),
                'theBooleanElement': settingBoolean(),
                'theCkEditorElement': settingLong(),
                'theTextAreaElement': settingTextareas(),
            }
        }
    ]


def setting__gallery__form(item=None):
    pages = []
    for page in Pages():
        pages.append({'label': page[1], 'id': page[0]})

    return [
        {
            'l': "صفحه",
            'n': 'page',
            'v': item.page if item else '',
            'id': 'PageElement',
            'r': 1,
            'data': pages,
            'c': 'col-md-8',
            'b': 'select2Single.html',
        },
        {
            'l': "وضعیت فعال",
            'n': 'is_active',
            'v': item.is_active if item else '',
            'id': 'theBooleanElement',
            'r': None,
            'c': 'col-md-2',
            'b': 'switch.html'
        }, {
            'l': "عکس",
            'n': 'photo',
            'v': item.photo if item else '',
            'id': 'thePhotoElement',
            'r': None,
            'c': 'col-md-4',
            'b': 'photo.html'
        }]


def setting__ad__form(item=None):
    positions = []
    for ac in adPosition():
        positions.append({'label': ac[1], 'id': ac[0]})

    return [
        {
            'l': "عنوان",
            'n': 'title',
            'v': item.title if item else '',
            'id': 'theTextElement',
            'r': None,
            'c': 'col-md-5',
            'b': 'textBox.html'
        },
        {
            'l': "لینک",
            'n': 'link',
            'v': item.link if item else '',
            'id': 'theLinkElement',
            'r': None,
            'c': 'col-md-5',
            'b': 'textBox.html'
        },
        {
            'l': "وضعیت فعال",
            'n': 'is_active',
            'v': item.is_active if item else '',
            'id': 'theBooleanElement',
            'r': None,
            'c': 'col-md-2',
            'b': 'switch.html'
        },
        {
            'l': "موقعیت",
            'n': 'position',
            'v': item.position if item else '',
            'id': 'settingSelectedTheItemposition',
            'r': None,
            'data': positions,
            'c': 'col-md-4',
            'b': 'select2Single.html',
        },
        {
            'l': "عکس",
            'n': 'photo',
            'v': item.photo if item else '',
            'id': 'thePhotoElement',
            'r': None,
            'c': 'col-md-4',
            'b': 'photo.html'
        },
        {
            'l': "تاریخ انقضا",
            'n': 'expireDate',
            'v': item.expireDate if item else None,
            'id': 'expireDateDayEl',
            'r': None,
            'c': 'col-md-4',
            'b': 'date.html'
        }
    ]
    

def setting__slider__form(item=None):
    return [
        {
            'l': "عنوان",
            'n': 'title',
            'v': item.title if item else '',
            'id': 'theTextElement',
            'r': None,
            'c': 'col-md-12',
            'b': 'textBox.html'
        }, {
            'l': "پاراگراف",
            'n': 'paragraph',
            'v': item.paragraph if item else '',
            'id': 'theparagraphElement',
            'r': None,
            'c': 'col-md-12',
            'b': 'textBox.html'
        }, {
            'l': "عکس",
            'n': 'photo',
            'v': item.photo if item else '',
            'id': 'thePhotoElement',
            'r': None,
            'c': 'col-md-4',
            'b': 'photo.html'
        }, {
            'l': "وضعیت فعال",
            'n': 'is_active',
            'v': item.is_active if item else '',
            'id': 'theBooleanElement',
            'r': None,
            'c': 'col-md-2',
            'b': 'switch.html'
        }
    ]


def setting__page__form(item=None):
    pages = []
    for ac in Pages():
        pages.append({'label': ac[1], 'id': ac[0]})

    return [{
        'l': "صفحه",
        'n': 'page',
        'v': item.page if item else '',
        'id': 'settingSelectedTheItem',
        'r': None,
        'data': pages,
        'c': 'col-md-4',
        'b': 'select2Single.html',
    }, {
        'l': "عنوان",
        'n': 'title',
        'v': item.title if item else '',
        'id': 'thetitle',
        'r': 1,
        'c': 'col-md-6',
        'b': 'textBox.html'
    }, {
        'l': "وضعیت فعال",
        'n': 'is_active',
        'v': item.is_active if item else '',
        'id': 'is_active',
        'r': None,
        'c': 'col-md-2',
        'b': 'switch.html'
    }, {
        'l': "خلاصه متن",
        'n': 'summer',
        'v': item.summer if item else '',
        'id': 'thesummer',
        'r': 1,
        'c': 'col-md-12',
        'b': 'textBox.html'
    }, {
        'l': "عنوان متا",
        'n': 'metaTitle',
        'v': item.metaTitle if item else '',
        'id': 'themetaTitle',
        'r': 1,
        'c': 'col-md-12',
        'b': 'textBox.html'
    }, {
        'l': "کلمات کلیدی متا",
        'n': 'metaKeywords',
        'v': item.metaKeywords if item else '',
        'id': 'themetaKeywords',
        'r': 1,
        'c': 'col-md-12',
        'b': 'textBox.html'
    }, {
        'l': "توضیحات متا",
        'n': 'metaDescription',
        'v': item.metaDescription if item else '',
        'id': 'themetaDescription',
        'r': 1,
        'c': 'col-md-12',
        'b': 'textBox.html'
    }, {
        'l': "عکس",
        'n': 'photo',
        'v': item.photo if item else '',
        'id': 'thefileElement',
        'r': None,
        'c': 'col-md-3',
        'b': 'photo.html'
    }, {
        'l': "گالری عکس",
        'n': 'gallery',
        'photos': item.gallery if item else [],
        'theItem': item if item else '',
        'id': 'theGalleryEl',
        'r': None,
        'removeRoute': "service/api/deletePhoto",
        'c': 'col-md-9',
        'b': 'photoMulti.html'
    }, {
        'class': 'col-md-12',
        "name": "faqs",
        "title": "پرسش و پاسخ",
        "keyLabel": "سوالات",
        "valueLabel": "پاسخ",
        "dataInitial": json.dumps(item.faqs) if item else [],
        'b': 'json-field.html'
    }, {
        'class': 'col-md-12',
        "name": "steps",
        "title": "مراحل",
        "keyLabel": "شماره",
        "valueLabel": "مورد",
        "dataInitial": json.dumps(item.steps) if item else [],
        'b': 'json-field.html'
    }, {
        'b': 'json-field-script.html'
    }, {
        'l': "متن",
        'n': 'text',
        'v': item.text if item else '',
        'id': 'textTinymce',
        'r': None,
        'c': 'col-md-12',
        'b': 'tinymceUse.html'
    }]


