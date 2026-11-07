# admin/app_fastapi/views/user/user_job_certificate.py

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from fastapi import APIRouter, Depends
import mimetypes

from app_fastapi.views.user.user_helper import get_current_user
from applications.user.models import User, JobCertificate
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.response import success_response, error_response
from app_fastapi.conf.fileManager import get_file_size, get_file_url, handle_save_file

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 مگابایت


# =========================================================
# سریالایزر
# =========================================================
def job_certificate_serialize(cert):
    if not cert:
        return None
    return {
        "id": cert.id,
        "type": cert.type,
        "type_display": cert.get_type_display(),
        "file": get_file_url(cert.file),
        "file_size": cert.file_size,
        "file_type": cert.file_type,
        "is_verified": cert.is_verified,
        "verified_at": cert.verified_at.isoformat() if cert.verified_at else None,
        "can_edit": not cert.is_verified,
        "created_at": cert.created_at.isoformat() if cert.created_at else None,
    }


# =========================================================
# دریافت همه مدارک کاربر
# =========================================================
@router.get("/profile/job-certificates/") # تغییر نام به جمع
async def get_job_certificates(user: User = Depends(get_current_user)):
    certs = await async_get_job_certificates(user)
    return success_response(
        "مدارک شغلی",
        await database_sync_to_async(lambda: [job_certificate_serialize(c) for c in certs])(),
    )


# =========================================================
# آپلود یا جایگزینی مدرک
# =========================================================
@router.post("/profile/job-certificate/upload/")
async def upload_job_certificate(
    form: dict = Depends(DependencyDataRequest),
    user: User = Depends(get_current_user),
):
    cert_type = form.get("type")
    file = form.get("file")

    if not file:
        return error_response("فایل الزامی است", status_code=400)

    valid_types = [c[0] for c in JobCertificate.FileType.choices]
    if cert_type not in valid_types:
        return error_response("نوع فایل معتبر نیست", status_code=400)

    file_size = get_file_size(file)
    if file_size > MAX_FILE_SIZE:
        return error_response("حجم فایل باید کمتر از 10 مگابایت باشد", status_code=400)

    # تشخیص نوع فایل
    mime_type = getattr(file, "content_type", None) or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

    cert, err = await async_upsert_job_certificate(user, cert_type, file, file_size, mime_type)
    if err:
        return error_response(err, status_code=403)

    return success_response(
        "ذخیره شد",
        await database_sync_to_async(job_certificate_serialize)(cert),
    )


# =========================================================
# حذف مدرک (بر اساس نوع)
# =========================================================
@router.delete("/profile/job-certificate/{cert_type}/") # اضافه شدن cert_type به مسیر
async def delete_job_certificate(cert_type: str, user: User = Depends(get_current_user)):
    ok, err = await async_delete_job_certificate(user, cert_type)
    if err:
        return error_response(err, status_code=403)
    if not ok:
        return error_response("یافت نشد", status_code=404)
    return success_response("حذف شد")


# =========================================================
# توابع کمکی پایگاه داده
# =========================================================
@database_sync_to_async
def async_get_job_certificates(user):
    return list(JobCertificate.objects.filter(user=user))


@sync_to_async
def async_upsert_job_certificate(user, cert_type, file, file_size, mime_type):
    # فقط مدرک با همین نوع را جستجو می‌کنیم
    cert = JobCertificate.objects.filter(user=user, type=cert_type).first()

    if cert and cert.is_verified:
        return None, "این مدرک قبلاً تأیید شده است؛ قابل جایگزینی نیست"

    if not cert:
        cert = JobCertificate(user=user, type=cert_type)

    cert.file.name = handle_save_file(file)
    cert.file_size = file_size
    cert.file_type = mime_type
    cert.is_verified = False
    cert.verified_at = None
    cert.save()
    return cert, None


@sync_to_async
def async_delete_job_certificate(user, cert_type):
    cert = JobCertificate.objects.filter(user=user, type=cert_type).first()
    if not cert:
        return False, None
    if cert.is_verified:
        return False, "این مدرک قبلاً تأیید شده است؛ قابل حذف نیست"
    cert.delete()
    return True, None