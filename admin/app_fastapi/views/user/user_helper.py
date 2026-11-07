# admin/app_fastapi/views/user/user_helper.py


from datetime import datetime, timedelta, timezone
from django.db import OperationalError, close_old_connections
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.utils.translation import gettext_lazy as _
from jose import jwt, JWTError, ExpiredSignatureError

from app_fastapi.conf.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from applications.user.models import User, RefreshToken

token_auth_scheme = HTTPBearer(auto_error=False)


###############################################
# JWT CREATE TOKENS
###############################################
async def create_access_token(data: dict, expires_delta=None):
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


async def create_refresh_token(user):
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    data = {"sub": user.username, "exp": expire, "type": "refresh"}
    encoded = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    await async_save_refresh_token(user, encoded, expire)
    return encoded


def create_reset_token(username: str):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def verify_reset_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
    except JWTError:
        return None


###############################################
# DEPENDENCIES (STANDARD & SECURE)
###############################################

def get_user_by_username(username: str):
    """
    کاربر را با روابط پرمصرف select_related برمی‌گرداند تا
    user_serialize بدون کوئری اضافی کار کند.
    """
    close_old_connections()
    try:
        return (
            User.objects
            .select_related(
                'relation_profile',
                'relation_score',
                'relation_received_invitation__inviter',
            )
            .prefetch_related(
                'relation_job_certificates',
            )
            .filter(username=username)
            .first()
        )
    except OperationalError:
        close_old_connections()
        return None


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme)):
    if not credentials:
        raise HTTPException(status_code=401, detail={"message": str(_("Authentication Required"))})
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=400, detail={"message": str(_("Token Not Valid"))})
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail={"message": str(_("Token Expired"))})
    except JWTError:
        raise HTTPException(status_code=400, detail={"message": str(_("Token Not Valid"))})

    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=400, detail={"message": str(_("Account Not Found"))})
    return user


def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme)):
    if not credentials:
        return None
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return None
    except (ExpiredSignatureError, JWTError):
        return None
    return get_user_by_username(username)


###############################################
# WS USER
###############################################
async def get_current_user_ws(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        return await sync_to_async(User.objects.get)(username=username)
    except User.DoesNotExist:
        raise HTTPException(status_code=401, detail="User not found")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


###############################################
# DB Async
###############################################
@database_sync_to_async
def async_save_refresh_token(user, token, expire):
    RefreshToken.objects.create(user=user, token=token, expires_at=expire)