from typing import Optional

from pydantic import BaseModel
from pydantic import BaseModel, Field, validator

from app_fastapi.schemas.base import BaseSchema


class DeviceSchema(BaseSchema):
    id: int
    device_name: str
    device_type: str
    ip_address: str
    last_login: str


class UserRegisterSchema(BaseModel):
    email: str
    password: str
    repassword: str
    username: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None


class BusinessRegisterSchema(BaseModel):
    email: str
    username: str
    password: str
    repassword: str
    business: int
    firstname: str
    lastname: str


class LoginSchema(BaseModel):
    email: str
    password: str


class LogoutSchema(BaseModel):
    refresh_token: str


class ForgetPasswordSchema(BaseModel):
    email: str


class RefreshSchema(BaseModel):
    refresh_token: str


class CheckEmailSchema(BaseModel):
    email: str


class CheckUsernameSchema(BaseModel):
    username: str
