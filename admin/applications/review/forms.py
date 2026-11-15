# applications/review/forms.py

from applications.core.forms import (
    make_date_item,
    make_input_item,
    make_select2_item,
    make_switch_item,
    pick_bool,
    pick_value,
)

from .models import ReviewAnswer, ReviewQuestion


def _answer_choices():
    return [{"id": v, "label": l} for v, l in ReviewAnswer.AnswerItem.choices]


# ═══════════════════════════════════════════════════════════
# QUESTION — Form
# ═══════════════════════════════════════════════════════════
def question__form(question=None, raw_data=None):
    return [
        make_input_item(
            label="متن سوال", name="question", input_id="id_question",
            kind="textarea", rows=3,
            value=pick_value(raw_data, question, "question"),
            placeholder="مثلاً: چقدر از خدمات ما راضی هستید؟",
            required=True, col_class="col-md-12",
        ),
        make_switch_item(
            label="فعال", name="is_active", input_id="id_is_active",
            value=pick_bool(raw_data, question, "is_active", default=True),
            col_class="col-md-6",
        ),
    ]


# ═══════════════════════════════════════════════════════════
# FILTERS — Questions
# ═══════════════════════════════════════════════════════════
def question__filters(get_data=None):
    def gv(key, default=""):
        return ((get_data.get(key) if get_data else None) or default)

    sort_choices = [
        {"id": "desc",         "label": "جدیدترین"},
        {"id": "asc",          "label": "قدیمی‌ترین"},
        {"id": "answers_desc", "label": "بیشترین پاسخ"},
        {"id": "answers_asc",  "label": "کمترین پاسخ"},
    ]
    count_choices = [
        {"id": "20",  "label": "20"},
        {"id": "50",  "label": "50"},
        {"id": "100", "label": "100"},
    ]
    active_choices = [
        {"id": "1", "label": "فعال"},
        {"id": "0", "label": "غیرفعال"},
    ]

    return {
        "basic": [
            make_input_item(
                label="جستجو", name="q", input_id="filter_q",
                value=gv("q"),
                placeholder="متن سوال…",
                col_class="col-md-4",
            ),
            make_select2_item(
                label="مرتب‌سازی", name="sort", input_id="filter_sort",
                choices=sort_choices, value=gv("sort", "desc"),
                empty_label=None, col_class="col-md-3",
            ),
            make_select2_item(
                label="تعداد نمایش", name="count", input_id="filter_count",
                choices=count_choices, value=gv("count", "20"),
                empty_label=None, col_class="col-md-2",
            ),
        ],
        "main": [
            make_select2_item(
                label="وضعیت", name="is_active", input_id="filter_is_active",
                choices=active_choices, value=gv("is_active"),
                empty_label="— همه —", col_class="col-md-6",
            ),
            make_date_item(
                label="ایجاد از", name="created_from", input_id="filter_created_from",
                value=gv("created_from"), col_class="col-md-6",
            ),
        ],
    }


# ═══════════════════════════════════════════════════════════
# FILTERS — Answers
# ═══════════════════════════════════════════════════════════
def answer__filters(get_data=None):
    def gv(key, default=""):
        return ((get_data.get(key) if get_data else None) or default)

    sort_choices = [
        {"id": "desc", "label": "جدیدترین"},
        {"id": "asc",  "label": "قدیمی‌ترین"},
    ]
    count_choices = [
        {"id": "50",  "label": "50"},
        {"id": "100", "label": "100"},
        {"id": "200", "label": "200"},
    ]

    question_choices = [
        {"id": q.pk, "label": q.question[:60]}
        for q in ReviewQuestion.objects.only("id", "question").order_by("-created_at")
    ]

    return {
        "basic": [
            make_input_item(
                label="جستجو", name="q", input_id="filter_q",
                value=gv("q"),
                placeholder="نام، موبایل کاربر، یا متن سوال…",
                col_class="col-md-4",
            ),
            make_select2_item(
                label="مرتب‌سازی", name="sort", input_id="filter_sort",
                choices=sort_choices, value=gv("sort", "desc"),
                empty_label=None, col_class="col-md-3",
            ),
            make_select2_item(
                label="تعداد نمایش", name="count", input_id="filter_count",
                choices=count_choices, value=gv("count", "50"),
                empty_label=None, col_class="col-md-2",
            ),
        ],
        "main": [
            make_select2_item(
                label="سوال", name="question", input_id="filter_question",
                choices=question_choices, value=gv("question"),
                empty_label="— همه —", col_class="col-md-6",
            ),
            make_select2_item(
                label="پاسخ", name="answer", input_id="filter_answer",
                choices=_answer_choices(), value=gv("answer"),
                empty_label="— همه —", col_class="col-md-6",
            ),
        ],
    }