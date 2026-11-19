# Path: app_fastapi/conf/schemas.py

from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
