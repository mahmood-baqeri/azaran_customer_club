# Path: applications/notification/forms.py

# applications/notification/forms.py

from applications.core.forms import (
    make_date_item,
    make_image_item,
    make_input_item,
    make_select2_item,
    pick_value,
)

from applications.user.models import User

from .models import Notification


# ═══════════════════════════════════════════════════════════
# NOTIFICATION — Form (create / edit)
# ═══════════════════════════════════════════════════════════
def notification__form(notification=None, raw_data=None):
    """items برای قالب عمومی form.html — نوتیفیکیشن."""

    # ─── گیرندگان فعلی ──────────────────────────────────
    if raw_data is not None:
        target_user_ids = raw_data.getlist("target_users") or []
    elif notification is not None:
        target_user_ids = list(
            notification.targets.values_list("user_id", flat=True)
        )
    else:
        target_user_ids = []

    # ─── لیست کاربران فعال ──────────────────────────────
    user_choices = [
        {
            "id": u.pk,
            "label": f"{u.full_name or u.mobile} — {u.mobile}",
        }
        for u in User.objects.filter(is_active=True)
        .only("id", "first_name", "last_name", "mobile", "username")
        .order_by("first_name", "last_name")
    ]

    target_type_choices = [
        {"id": v, "label": l} for v, l in Notification.TargetType.choices
    ]
    type_choices = [
        {"id": v, "label": l} for v, l in Notification.NotificationType.choices
    ]
    priority_choices = [
        {"id": v, "label": l} for v, l in Notification.Priority.choices
    ]

    return [
        # ─── محتوا ──────────────────────────────────────
        make_input_item(
            label="عنوان", name="title", input_id="id_title",
            value=pick_value(raw_data, notification, "title"),
            required=True, col_class="col-md-8",
        ),
        make_select2_item(
            label="نوع نوتیفیکیشن", name="notification_type", input_id="id_notification_type",
            choices=type_choices,
            value=pick_value(raw_data, notification, "notification_type", "system"),
            required=True, empty_label=None, col_class="col-md-4",
        ),
        make_input_item(
            label="متن", name="body", input_id="id_body",
            kind="textarea", rows=5,
            value=pick_value(raw_data, notification, "body"),
            required=True, col_class="col-md-12",
        ),
        make_image_item(
            label="تصویر", name="image", input_id="id_image",
            title="انتخاب تصویر",
            existing=notification.image if notification else None,
            col_class="col-md-6",
        ),
        make_select2_item(
            label="اولویت", name="priority", input_id="id_priority",
            choices=priority_choices,
            value=pick_value(raw_data, notification, "priority", "normal"),
            required=True, empty_label=None, col_class="col-md-6",
        ),

        # ─── هدف‌گیری ────────────────────────────────────
        make_select2_item(
            label="نوع هدف‌گیری", name="target_type", input_id="id_target_type",
            choices=target_type_choices,
            value=pick_value(raw_data, notification, "target_type", "user"),
            required=True, empty_label=None, col_class="col-md-4",
        ),
        make_select2_item(
            label="کاربران هدف", name="target_users", input_id="id_target_users",
            choices=user_choices,
            value=target_user_ids,
            multiple=True,
            empty_label="",
            placeholder="کاربران را انتخاب کنید…",
            col_class="col-md-8",
        ),

        # ─── اقدام (deep link) ──────────────────────────
        make_input_item(
            label="نوع اقدام (اختیاری)", name="action_type", input_id="id_action_type",
            value=pick_value(raw_data, notification, "action_type"),
            placeholder="مثلاً: open_gift، open_order",
            col_class="col-md-4",
        ),
        make_input_item(
            label="لینک اقدام (اختیاری)", name="action_url", input_id="id_action_url",
            value=pick_value(raw_data, notification, "action_url"),
            placeholder="https://…",
            col_class="col-md-8",
        ),

        # ─── زمان‌بندی ──────────────────────────────────
        make_date_item(
            label="تاریخ ارسال (خالی = دستی)",
            name="scheduled_at",
            input_id="id_scheduled_at",
            value=pick_value(raw_data, notification, "scheduled_at"),
            col_class="col-md-6",
        ),
        make_date_item(
            label="تاریخ انقضا",
            name="expires_at",
            input_id="id_expires_at",
            value=pick_value(raw_data, notification, "expires_at"),
            col_class="col-md-6",
        ),
    ]


# ═══════════════════════════════════════════════════════════
# NOTIFICATION — Filters
# ═══════════════════════════════════════════════════════════
def notification__filters(get_data=None):
    """items فیلترهای لیست نوتیفیکیشن‌ها."""

    def gv(key, default=""):
        return ((get_data.get(key) if get_data else None) or default)

    sort_choices = [
        {"id": "desc",      "label": "جدیدترین"},
        {"id": "asc",       "label": "قدیمی‌ترین"},
        {"id": "sent_desc", "label": "تازه‌ترین ارسال"},
    ]
    count_choices = [
        {"id": "20",  "label": "20"},
        {"id": "50",  "label": "50"},
        {"id": "100", "label": "100"},
    ]
    status_choices = [
        {"id": v, "label": l} for v, l in Notification.Status.choices
    ]
    target_choices = [
        {"id": v, "label": l} for v, l in Notification.TargetType.choices
    ]
    type_choices = [
        {"id": v, "label": l} for v, l in Notification.NotificationType.choices
    ]
    priority_choices = [
        {"id": v, "label": l} for v, l in Notification.Priority.choices
    ]

    return {
        "basic": [
            make_input_item(
                label="جستجو", name="q", input_id="filter_q",
                value=gv("q"),
                placeholder="عنوان، متن، نام یا موبایل گیرنده…",
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
                label="وضعیت", name="status", input_id="filter_status",
                choices=status_choices, value=gv("status"),
                empty_label="— همه —", col_class="col-md-3",
            ),
            make_select2_item(
                label="نوع هدف‌گیری", name="target_type", input_id="filter_target_type",
                choices=target_choices, value=gv("target_type"),
                empty_label="— همه —", col_class="col-md-3",
            ),
            make_select2_item(
                label="نوع نوتیفیکیشن", name="notification_type", input_id="filter_notification_type",
                choices=type_choices, value=gv("notification_type"),
                empty_label="— همه —", col_class="col-md-3",
            ),
            make_select2_item(
                label="اولویت", name="priority", input_id="filter_priority",
                choices=priority_choices, value=gv("priority"),
                empty_label="— همه —", col_class="col-md-3",
            ),
        ],
        "advanced": [
            {
                "title": "فیلترهای بیشتر",
                "items": [
                    make_date_item(
                        label="ارسال از", name="sent_from", input_id="filter_sent_from",
                        value=gv("sent_from"), col_class="col-md-3",
                    ),
                    make_date_item(
                        label="ارسال تا", name="sent_to", input_id="filter_sent_to",
                        value=gv("sent_to"), col_class="col-md-3",
                    ),
                    make_date_item(
                        label="ایجاد از", name="created_from", input_id="filter_created_from",
                        value=gv("created_from"), col_class="col-md-3",
                    ),
                    make_date_item(
                        label="ایجاد تا", name="created_to", input_id="filter_created_to",
                        value=gv("created_to"), col_class="col-md-3",
                    ),
                ],
            },
        ],
    }