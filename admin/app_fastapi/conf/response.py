from django.db.models.fields.files import FieldFile
from fastapi.responses import JSONResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from PIL.Image import Image
from django.db.models import Model, QuerySet
import json


def success_response(message: str, data=None, help_data=None):
    return JSONResponse(
        status_code=200,
        content=json.loads(json.dumps({
            "status": "Success",
            "message": message,
            "data": data or {},
            "help_data": help_data or {}
        }, cls=DjangoJSONEncoder))
    )


def error_response(message: str, status_code: int = 400, error_code: str = None, data=None, help_data=None):
    content = {
        "status": "Error",
        "message": message,
        "data": data or {},
        "help_data": help_data or {},
    }
    if error_code:
        content["error_code"] = error_code
    return JSONResponse(status_code=status_code, content=content)


def validation_error_response(errors: list):
    return JSONResponse(
        status_code=422,
        content={
            "status": "Errors",
            "errors": errors,
        }
    )
