# Path: app_fastapi/schemas/base.py

from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
