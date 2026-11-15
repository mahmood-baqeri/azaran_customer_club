# applications/factor/repositories.py

import logging

from django.db import transaction

from .models import Factor
from .services import (
    FactorError,
    approve_factor,
    create_factor,
    reject_factor,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# FACTOR — Store
# ═══════════════════════════════════════════════════════════
def factor__store(request, cleaned, user, item=None):
    """Create از services؛ Update مستقیم (فقط PENDING)."""
    if item is None:
        upload = cleaned["photo"]
        return create_factor(
            user=user,
            photo_file_name=upload,
            amount=cleaned.get("amount"),
            invoice_number=cleaned.get("invoice_number"),
            invoice_issue_at=cleaned.get("invoice_issue_at"),
            number_water_taps=cleaned.get("number_water_taps"),
            number_connections=cleaned.get("number_connections"),
            pipe_length=cleaned.get("pipe_length"),
            shop_name=cleaned.get("shop_name"),
            seller_phone=cleaned.get("seller_phone"),
            seller_address=cleaned.get("seller_address"),
        )

    if item.status != Factor.Status.PENDING:
        raise FactorError("فقط فاکتورهای در انتظار قابل ویرایش هستند")

    item.amount = cleaned.get("amount")
    item.invoice_number = cleaned.get("invoice_number")
    item.invoice_issue_at = cleaned.get("invoice_issue_at")
    item.number_water_taps = cleaned.get("number_water_taps")
    item.number_connections = cleaned.get("number_connections")
    item.pipe_length = cleaned.get("pipe_length")
    item.shop_name = cleaned.get("shop_name")
    item.seller_phone = cleaned.get("seller_phone")
    item.seller_address = cleaned.get("seller_address")

    upload = cleaned.get("photo")
    if upload:
        item.photo = upload

    item.save()
    return item


# ═══════════════════════════════════════════════════════════
# FACTOR — Actions
# ═══════════════════════════════════════════════════════════
def factor__approve(factor_id, admin):
    return approve_factor(factor_id, admin)


def factor__reject(factor_id, admin, reason):
    return reject_factor(factor_id, admin, reason=reason)


@transaction.atomic
def factor__delete(factor_id):
    factor = Factor.objects.select_for_update().filter(id=factor_id).first()
    if not factor:
        raise FactorError("فاکتور یافت نشد")
    if factor.status == Factor.Status.APPROVED:
        raise FactorError("فاکتورهای تأیید شده قابل حذف نیستند")
    factor.delete()