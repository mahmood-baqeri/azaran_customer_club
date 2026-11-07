# applications/factor/services.py

import logging
import re
from typing import Optional

from django.db import transaction
from django.utils import timezone

from applications.factor.models import Factor
from applications.score import api as score_api
from applications.score.models import UserScoreLog
from applications.user.models import User

logger = logging.getLogger(__name__)


class FactorError(Exception):
    """خطای منطقی فاکتور (پیام فارسی برای کاربر)."""


# ═══════════════════════════════════════════════════════════
# ایجاد فاکتور
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def create_factor(
    user: User,
    *,
    photo_file_name: str,
    amount: Optional[int] = None,
    invoice_number: Optional[str] = None,
    invoice_issue_at=None,
    number_water_taps: Optional[int] = None,
    number_connections: Optional[int] = None,
    pipe_length: Optional[int] = None,
    shop_name: Optional[str] = None,
    seller_phone: Optional[str] = None,
    seller_address: Optional[str] = None,
) -> Factor:
    """
    ساخت فاکتور جدید با وضعیت PENDING.

    اعتبارسنجی:
    - amount اگه داده شد، > 0
    - invoice_issue_at در آینده نباشه
    - invoice_number اگه داده شد، یکتا
    - seller_phone فرمت معتبر
    """
    # ── ۱) مبلغ ──────────────────────────────────────
    if amount is not None and amount <= 0:
        raise FactorError("مبلغ فاکتور باید بزرگ‌تر از صفر باشد")

    # ── ۲) تاریخ صدور ────────────────────────────────
    if invoice_issue_at and invoice_issue_at > timezone.now():
        raise FactorError("تاریخ صدور فاکتور نمی‌تواند در آینده باشد")

    # ── ۳) شماره فاکتور ──────────────────────────────
    if invoice_number:
        invoice_number = invoice_number.strip()
        if Factor.objects.filter(invoice_number=invoice_number).exists():
            raise FactorError("این شماره فاکتور قبلاً ثبت شده است")

    # ── ۴) تلفن فروشنده ──────────────────────────────
    if seller_phone:
        seller_phone = seller_phone.strip()
        if not (
            re.match(r"^09\d{9}$", seller_phone)
            or re.match(r"^0\d{2,3}\d{7,8}$", seller_phone)
        ):
            raise FactorError("فرمت تلفن فروشنده نامعتبر است")

    # ── ۵) ساخت فاکتور ──────────────────────────────
    factor = Factor.objects.create(
        user=user,
        invoice_number=invoice_number,
        photo=photo_file_name,
        amount=amount,
        invoice_issue_at=invoice_issue_at,
        number_water_taps=number_water_taps,
        number_connections=number_connections,
        pipe_length=pipe_length,
        shop_name=shop_name,
        seller_phone=seller_phone,
        seller_address=seller_address,
        status=Factor.Status.PENDING,
    )
    return factor


# ═══════════════════════════════════════════════════════════
# تأیید فاکتور (فقط ادمین) — امتیازدهی
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def approve_factor(
    factor_id: int,
    admin: User,
    *,
    auto_award: bool = True,
) -> Factor:
    factor = (
        Factor.objects
        .select_for_update()
        .select_related("user")
        .filter(id=factor_id)
        .first()
    )
    if not factor:
        raise FactorError("فاکتور یافت نشد")
    if factor.status == Factor.Status.APPROVED:
        raise FactorError("فاکتور قبلاً تأیید شده است")
    if factor.status == Factor.Status.REJECTED:
        raise FactorError("فاکتور رد شده و قابل تأیید نیست")

    # چون امتیاز INVOICE بر اساس amount محاسبه می‌شه
    if auto_award and (factor.amount is None or factor.amount <= 0):
        raise FactorError("برای تأیید فاکتور، مبلغ فاکتور باید ثبت شده باشد")

    factor.status = Factor.Status.APPROVED
    factor.approved_by = admin
    factor.approved_at = timezone.now()
    factor.save(update_fields=["status", "approved_by", "approved_at"])

    if auto_award:
        _award_factor_scores(factor)

    return factor


def _award_factor_scores(factor: Factor) -> None:
    """
    امتیاز INVOICE به ثبت‌کننده.
    base_value = مبلغ فاکتور → PERCENT در ScoreRule.
    """
    owner_log = score_api.award(
        factor.user,
        UserScoreLog.TransactionCode.INVOICE,
        base_value=int(factor.amount),
        reference_type="factor",
        reference_id=str(factor.id),
        reason=f"تأیید فاکتور #{factor.invoice_number or factor.id}",
        extra={
            "factor_id": factor.id,
            "invoice_amount": int(factor.amount),
        },
        strict=True,
    )

    logger.info(
        "INVOICE award: factor=%s user=%s amount=%s points=%s",
        factor.id, factor.user_id, factor.amount,
        owner_log.amount if owner_log else 0,
    )


# ═══════════════════════════════════════════════════════════
# رد فاکتور
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def reject_factor(factor_id: int, admin: User, *, reason: str) -> Factor:
    if not reason or not reason.strip():
        raise FactorError("دلیل رد الزامی است")

    factor = (
        Factor.objects
        .select_for_update()
        .filter(id=factor_id)
        .first()
    )
    if not factor:
        raise FactorError("فاکتور یافت نشد")
    if factor.status != Factor.Status.PENDING:
        raise FactorError("فقط فاکتورهای در انتظار قابل رد هستند")

    factor.status = Factor.Status.REJECTED
    factor.rejection_reason = reason.strip()
    factor.rejected_at = timezone.now()
    factor.save(update_fields=["status", "rejection_reason", "rejected_at"])
    return factor