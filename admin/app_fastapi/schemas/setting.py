from typing import Optional

from pydantic import BaseModel, HttpUrl
from typing import Union, Literal, Optional
from app_fastapi.schemas.base import BaseSchema


class SliderSchema(BaseSchema):
    title: Optional[str] = None
    link: Optional[str] = None
    photo: Optional[str] = None


class CitySchema(BaseSchema):
    id: int
    name: Optional[str] = None
    photo: Optional[str] = None


class LanguageSchema(BaseSchema):
    id: int
    title: Optional[str] = None


class AdSchema(BaseSchema):
    id: int
    title: Optional[str] = None
    photo: Optional[str] = None
    link: Optional[str] = None


class SettingSchema(BaseSchema):
    id: int
    value: Union[str, int, float, HttpUrl]



