from typing import Optional
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, validator

from app_fastapi.schemas.base import BaseSchema


class CategorySchema(BaseSchema):
    id: int
    title: str
    photo: Optional[str] = None
    



