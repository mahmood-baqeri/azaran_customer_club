# Path: applications/setting/forms.py

import json
from applications.core.keyValue import (
    appSettings, adPosition, Pages,
    settingPhoto, settingNumbers, settingBoolean, settingLong, settingTextareas,
)
from applications.core.forms import (
    make_input_item, make_select2_item, make_switch_item,
    make_image_item, make_date_item,
    pick_value, pick_bool,
)



# ─────────────────────────────────────────────────────────
# تنظیمات (setting)
# ─────────────────────────────────────────────────────────
def setting__setting__form(item=None, raw_data=None):
    choices = [{'id': ac[0], 'label': ac[1]} for ac in appSettings()]

    return [
        make_select2_item(
            label='گزینه', name='key',
            choices=choices,
            value=pick_value(raw_data, item, 'key'),
            required=True, col_class='col-md-4',
            input_id='settingSelectedTheItem',
        ),
        make_image_item(
            label='تصویر', name='photo',
            existing=item.value_file if item else None,
            col_class='col-md-4 theSettingItemRoot d-none',
            input_id='thePhotoElement',
        ),
        make_input_item(
            label='عدد', name='value_number', kind='number',
            value=pick_value(raw_data, item, 'value_text'),
            col_class='col-md-4 theSettingItemRoot d-none',
            input_id='theNumberElement',
        ),
        make_input_item(
            label='متن', name='value_text',
            value=pick_value(raw_data, item, 'value_text'),
            col_class='col-md-8 theSettingItemRoot d-none',
            input_id='theTextElement',
        ),
        make_input_item(
            label='متن کوتاه', name='value_textarea', kind='textarea',
            value=pick_value(raw_data, item, 'value_text'),
            rows=4, col_class='col-md-12 theSettingItemRoot d-none',
            input_id='theTextAreaElement',
        ),
        {
            'l': "متن" + " " + "طولانی",
            'n': '',
            'v': item.value_text if item else '',
            'id': 'theCkEditorElement',
            'r': None,
            'c': 'col-md-12 theSettingItemRoot d-none',
            'b': 'tinymceUseForSetting.html'
        },
        make_switch_item(
            label='وضعیت فعال', name='value_boolean',
            value=pick_bool(raw_data, item, 'value_text'),
            col_class='col-md-4 theSettingItemRoot d-none',
            input_id='theBooleanElement',
        ),
        # بلوک مدیریت گروه‌های تنظیمات (ساختار ثابت قدیمی)
        {
            'b': 'manageSetting.html',
            'settingGroups': {
                'thePhotoElement':     settingPhoto(),
                'theNumberElement':    settingNumbers(),
                'theBooleanElement':   settingBoolean(),
                'theCkEditorElement':  settingLong(),
                'theTextAreaElement':  settingTextareas(),
            },
        },
    ]



# ─────────────────────────────────────────────────────────
# گالری (gallery)
# ─────────────────────────────────────────────────────────
def setting__gallery__form(item=None, raw_data=None):
    pages = [{'id': p[0], 'label': p[1]} for p in Pages()]

    return [
        make_select2_item(
            label='صفحه', name='page',
            choices=pages,
            value=pick_value(raw_data, item, 'page'),
            required=True, col_class='col-md-8',
        ),
        make_switch_item(
            label='وضعیت فعال', name='is_active',
            value=pick_bool(raw_data, item, 'is_active', default=True),
            col_class='col-md-2',
        ),
        make_image_item(
            label='عکس', name='photo',
            existing=item.photo if item else None,
            col_class='col-md-4',
        ),
    ]



# ─────────────────────────────────────────────────────────
# تبلیغات (ad)
# ─────────────────────────────────────────────────────────
def setting__ad__form(item=None, raw_data=None):
    positions = [{'id': ac[0], 'label': ac[1]} for ac in adPosition()]

    return [
        make_input_item(
            label='عنوان', name='title',
            value=pick_value(raw_data, item, 'title'),
            required=True, col_class='col-md-5',
            input_id='theTextElement',
        ),
        make_input_item(
            label='لینک', name='link',
            value=pick_value(raw_data, item, 'link'),
            col_class='col-md-5',
            input_id='theLinkElement',
        ),
        make_switch_item(
            label='وضعیت فعال', name='is_active',
            value=pick_bool(raw_data, item, 'is_active', default=True),
            col_class='col-md-2',
            input_id='theBooleanElement',
        ),
        make_select2_item(
            label='موقعیت', name='position',
            choices=positions,
            value=pick_value(raw_data, item, 'position'),
            required=True, col_class='col-md-4',
            input_id='settingSelectedTheItemposition',
        ),
        make_image_item(
            label='عکس', name='photo',
            existing=item.photo if item else None,
            col_class='col-md-4',
            input_id='thePhotoElement',
        ),
        make_date_item(
            label='تاریخ انقضا', name='expireDate',
            value=pick_value(raw_data, item, 'expireDate'),
            col_class='col-md-4',
            input_id='expireDateDayEl',
        ),
    ]
    



# ─────────────────────────────────────────────────────────
# اسلایدر (slider)
# ─────────────────────────────────────────────────────────
def setting__slider__form(item=None, raw_data=None):
    return [
        make_input_item(
            label='عنوان', name='title',
            value=pick_value(raw_data, item, 'title'),
            required=True, col_class='col-md-12',
            input_id='theTextElement',
        ),
        make_input_item(
            label='پاراگراف', name='paragraph',
            value=pick_value(raw_data, item, 'paragraph'),
            col_class='col-md-12',
            input_id='theparagraphElement',
        ),
        make_image_item(
            label='عکس', name='photo',
            existing=item.photo if item else None,
            col_class='col-md-4',
            input_id='thePhotoElement',
        ),
        make_switch_item(
            label='وضعیت فعال', name='is_active',
            value=pick_bool(raw_data, item, 'is_active', default=True),
            col_class='col-md-2',
            input_id='theBooleanElement',
        ),
    ]


# ─────────────────────────────────────────────────────────
# صفحه (page)
# ─────────────────────────────────────────────────────────
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


